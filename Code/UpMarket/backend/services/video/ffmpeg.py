"""FFmpeg helpers: last-frame extraction, concatenation, audio mixing, probing."""
import json
import os
import subprocess
import tempfile
from pathlib import Path

FFMPEG = os.getenv("FFMPEG_BIN", "ffmpeg")
FFPROBE = os.getenv("FFPROBE_BIN", "ffprobe")


class VideoProcessingError(Exception):
    pass


def _run(cmd):
    try:
        result = subprocess.run(
            cmd, capture_output=True, encoding="utf-8", errors="replace"
        )
    except FileNotFoundError as exc:
        raise VideoProcessingError(
            f"{cmd[0]} binary not found — install ffmpeg or set FFMPEG_BIN/FFPROBE_BIN"
        ) from exc
    if result.returncode != 0:
        tail = (result.stderr or "")[-2000:]
        raise VideoProcessingError(f"Command failed ({cmd[0]}): {tail}")
    return result


def extract_last_frame(video_path, out_path) -> Path:
    """Extract the final frame of a video — the anchor for the next segment."""
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    # Fast path: seek near the end. The offset must exceed one frame interval,
    # so try progressively larger offsets before falling back.
    for offset in ("-0.3", "-1"):
        try:
            _run([FFMPEG, "-y", "-sseof", offset, "-i", str(video_path),
                  "-frames:v", "1", "-q:v", "1", str(out)])
        except VideoProcessingError:
            continue
        if out.exists() and out.stat().st_size > 0:
            return out
    # Robust fallback: decode all frames, keep overwriting one image → last frame.
    _run([FFMPEG, "-y", "-i", str(video_path), "-update", "1", "-q:v", "1", str(out)])
    if not out.exists() or out.stat().st_size == 0:
        raise VideoProcessingError(f"Last frame was not written: {out}")
    return out


def probe(path) -> dict:
    result = _run([FFPROBE, "-v", "error", "-print_format", "json",
                   "-show_format", "-show_streams", str(path)])
    return json.loads(result.stdout)


def probe_duration(path) -> float:
    info = probe(path)
    try:
        return float(info["format"]["duration"])
    except (KeyError, TypeError, ValueError) as exc:
        raise VideoProcessingError(f"Could not read duration of {path}") from exc


def concat_videos(video_paths, out_path) -> Path:
    """Concatenate same-codec segments losslessly; re-encode as fallback."""
    if not video_paths:
        raise VideoProcessingError("No video segments to concatenate")
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(
        "w", suffix=".txt", delete=False, encoding="utf-8"
    ) as fh:
        for path in video_paths:
            escaped = str(Path(path).resolve()).replace("'", "'\\''")
            fh.write(f"file '{escaped}'\n")
        list_file = fh.name
    try:
        try:
            _run([FFMPEG, "-y", "-f", "concat", "-safe", "0",
                  "-i", list_file, "-c", "copy", str(out)])
        except VideoProcessingError:
            # mismatched parameters → re-encode
            _run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", list_file,
                  "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", str(out)])
    finally:
        os.unlink(list_file)
    return out


def mix_audio(video_path, audio_path, out_path) -> Path:
    """Mux narration audio onto a video without re-encoding the video stream."""
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    _run([FFMPEG, "-y", "-i", str(video_path), "-i", str(audio_path),
          "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac",
          "-shortest", str(out)])
    return out


def make_silence(duration, out_path, sample_rate=24000) -> Path:
    """Generate a silent audio clip (for scenes without narration)."""
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    _run([FFMPEG, "-y", "-f", "lavfi", "-i", f"anullsrc=r={sample_rate}:cl=mono",
          "-t", str(duration), "-c:a", "aac", str(out)])
    return out


def fit_audio(audio_path, out_path, target_duration, max_tempo=1.25) -> Path:
    """Fit narration into a scene window: speed up (capped), pad, trim to exact length.

    Never hard-cuts mid-speech unless the narration exceeds target*max_tempo;
    in that case the overflow is trimmed and the caller should record a warning.
    """
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    duration = probe_duration(audio_path)
    filters = []
    if duration > target_duration + 0.05:
        tempo = min(duration / target_duration, max_tempo)
        filters.append(f"atempo={tempo:.4f}")
    filters.append("apad")
    _run([FFMPEG, "-y", "-i", str(audio_path), "-af", ",".join(filters),
          "-t", str(target_duration), "-c:a", "aac", str(out)])
    return out


def concat_audio(audio_paths, out_path) -> Path:
    """Concatenate audio clips via the concat filter (codec-agnostic)."""
    if not audio_paths:
        raise VideoProcessingError("No audio clips to concatenate")
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [FFMPEG, "-y"]
    for path in audio_paths:
        cmd += ["-i", str(path)]
    cmd += [
        "-filter_complex",
        f"concat=n={len(audio_paths)}:v=0:a=1",
        "-c:a", "aac",
        str(out),
    ]
    _run(cmd)
    return out
