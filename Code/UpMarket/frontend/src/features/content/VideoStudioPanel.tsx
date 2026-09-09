import { useCallback, useEffect, useState } from "react";

import { api, errorMessage } from "../../api/client";
import JobProgress from "../../components/JobProgress";
import {
  Button,
  Card,
  Chip,
  ErrorBox,
  Field,
  Input,
  SectionTitle,
} from "../../components/ui";
import { useJobRunner } from "../../hooks/useJobRunner";
import { Job, VideoScriptInfo } from "../../types";

const TRANSITION_LABEL: Record<string, string> = {
  NEW_SCENE: "صحنه جدید",
  CONTINUE: "ادامه از فریم آخر",
  TRANSITION: "گذار نرم",
};

const SEGMENT_STATE: Record<string, string> = {
  PENDING: "در انتظار",
  GENERATING: "در حال تولید",
  DONE: "آماده ✓",
  FAILED: "خطا ✗",
};

export default function VideoStudioPanel({ productId }: { productId: number }) {
  const [script, setScript] = useState<VideoScriptInfo | null>(null);
  const [duration, setDuration] = useState("15");
  const [objective, setObjective] = useState("");
  const [language, setLanguage] = useState<"fa" | "en">("fa");
  const [showScenes, setShowScenes] = useState(false);

  const load = useCallback(async () => {
    try {
      // the backend returns 200 + null when no script exists yet
      const { data } = await api.get<VideoScriptInfo | null>(
        `/products/${productId}/video-script/`,
      );
      setScript(data ?? null);
    } catch {
      setScript(null);
    }
  }, [productId]);

  useEffect(() => {
    void load();
  }, [load]);

  const scriptRunner = useJobRunner(load);
  const videoRunner = useJobRunner(load);
  const voiceRunner = useJobRunner(load);

  // re-attach to in-flight jobs after refresh/navigation (beter.md #2)
  const resumeScript = scriptRunner.resume;
  const resumeVideo = videoRunner.resume;
  const resumeVoice = voiceRunner.resume;
  useEffect(() => {
    void resumeScript({ type: "video_script_generation", productId });
  }, [resumeScript, productId]);
  useEffect(() => {
    if (!script?.id) return;
    void resumeVideo({ type: "video_generation", scriptId: script.id });
    void resumeVoice({ type: "voice_generation", scriptId: script.id });
  }, [resumeVideo, resumeVoice, script?.id]);

  const generateScript = async () => {
    scriptRunner.begin();
    try {
      const { data } = await api.post<{ job_id: number; job: Job }>(
        `/products/${productId}/video-script/`,
        { duration: Number(duration) || 15, objective, language },
      );
      scriptRunner.track(data.job_id, data.job);
    } catch (err) {
      scriptRunner.fail(errorMessage(err));
    }
  };

  const generateVideo = async () => {
    if (!script) return;
    videoRunner.begin();
    try {
      const { data } = await api.post<{ job_id: number; job: Job }>(
        `/video-scripts/${script.id}/generate/`,
      );
      videoRunner.track(data.job_id, data.job);
    } catch (err) {
      videoRunner.fail(errorMessage(err));
    }
  };

  const generateVoice = async () => {
    if (!script) return;
    voiceRunner.begin();
    try {
      const { data } = await api.post<{ job_id: number; job: Job }>(
        `/video-scripts/${script.id}/voice/`,
      );
      voiceRunner.track(data.job_id, data.job);
    } catch (err) {
      voiceRunner.fail(errorMessage(err));
    }
  };

  const anyRunning = scriptRunner.running || videoRunner.running || voiceRunner.running;
  const activeRunner = [voiceRunner, videoRunner, scriptRunner].find((r) => r.running) ?? null;
  const activeJob = activeRunner?.job ?? null;

  return (
    <Card>
      <SectionTitle>🎬 استودیوی ویدیو</SectionTitle>
      <ErrorBox message={scriptRunner.error} />
      <ErrorBox message={videoRunner.error} />
      <ErrorBox message={voiceRunner.error} />

      <div className="mb-4 flex flex-wrap items-end gap-3">
        <div className="w-32">
          <Field label="مدت (ثانیه)">
            <Input
              type="number"
              min="5"
              max="60"
              step="5"
              value={duration}
              onChange={(e) => setDuration(e.target.value)}
            />
          </Field>
        </div>
        <div className="w-64">
          <Field label="هدف (اختیاری)">
            <Input
              value={objective}
              onChange={(e) => setObjective(e.target.value)}
              placeholder="مثلاً معرفی محصول جدید"
            />
          </Field>
        </div>
        <div className="w-40">
          <Field label="زبان نریشن و صدا">
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value as "fa" | "en")}
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm focus:border-violet-500 focus:outline-none focus:ring-2 focus:ring-violet-200"
            >
              <option value="fa">🇮🇷 فارسی</option>
              <option value="en">🇬🇧 English</option>
            </select>
          </Field>
        </div>
        <Button onClick={generateScript} disabled={anyRunning}>
          {scriptRunner.running ? "در حال نوشتن سناریو…" : script ? "سناریوی جدید" : "تولید سناریو"}
        </Button>
        {script && (
          <Button onClick={generateVideo} disabled={anyRunning} variant="secondary">
            {videoRunner.running ? "در حال تولید ویدیو…" : "🎥 تولید ویدیو (Wan 2.2)"}
          </Button>
        )}
        {script?.final_video && (
          <Button onClick={generateVoice} disabled={anyRunning} variant="secondary">
            {voiceRunner.running ? "در حال صداگذاری…" : "🔊 صداگذاری"}
          </Button>
        )}
      </div>

      {anyRunning && (
        <JobProgress
          job={activeJob}
          startedAt={activeRunner?.startedAt ?? null}
          onCancel={() => void activeRunner?.cancel()}
          fallbackLabel="در حال شروع پردازش ویدیو…"
        />
      )}

      {!script && !anyRunning && (
        <p className="text-sm text-slate-400">
          هنوز سناریویی ساخته نشده. اول سناریو تولید کنید؛ بعد ویدیو قطعه‌قطعه با Wan 2.2 ساخته
          می‌شود (نیازمند ComfyUI روی سیستم اصلی + حداقل یک عکس محصول).
        </p>
      )}

      {script && (
        <div className="space-y-4">
          {script.concept && (
            <p className="rounded-lg bg-slate-50 p-3 text-sm leading-6 text-slate-700">
              <span className="font-bold">کانسپت: </span>
              {script.concept}
            </p>
          )}
          {script.cta && (
            <p className="text-sm text-violet-700">
              <span className="font-bold">CTA: </span>
              {script.cta}
            </p>
          )}

          <div className="flex items-center gap-3 text-sm">
            <Chip>{script.total_duration} ثانیه</Chip>
            <Chip>{script.scenes.length} صحنه</Chip>
            <Chip>{script.narration_language === "en" ? "🇬🇧 نریشن انگلیسی" : "🇮🇷 نریشن فارسی"}</Chip>
            <button
              onClick={() => setShowScenes((v) => !v)}
              className="text-violet-600 hover:underline"
            >
              {showScenes ? "بستن صحنه‌ها" : "نمایش صحنه‌ها"}
            </button>
          </div>

          {showScenes && (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[600px] text-right text-sm">
                <thead>
                  <tr className="border-b border-slate-200 text-xs text-slate-500">
                    <th className="py-2">#</th>
                    <th>مدت</th>
                    <th>ترنزیشن</th>
                    <th>نریشن</th>
                    <th>پرامپت بصری (EN)</th>
                  </tr>
                </thead>
                <tbody>
                  {script.scenes.map((scene) => (
                    <tr key={scene.index} className="border-b border-slate-100 align-top">
                      <td className="py-2 font-bold">{scene.index}</td>
                      <td>{scene.duration}s</td>
                      <td className="text-xs">{TRANSITION_LABEL[scene.transition]}</td>
                      <td className="max-w-[200px]">{scene.narration}</td>
                      <td className="max-w-[260px] text-xs text-slate-500" dir="ltr">
                        {scene.visual_prompt}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {script.segments.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {script.segments.map((segment) => (
                <span
                  key={segment.index}
                  className={`rounded-full px-3 py-1 text-xs ${
                    segment.status === "DONE"
                      ? "bg-green-100 text-green-800"
                      : segment.status === "FAILED"
                        ? "bg-red-100 text-red-700"
                        : segment.status === "GENERATING"
                          ? "bg-amber-100 text-amber-800"
                          : "bg-slate-100 text-slate-500"
                  }`}
                  title={segment.error || segment.anchor_source}
                >
                  قطعه {segment.index}: {SEGMENT_STATE[segment.status]}
                </span>
              ))}
            </div>
          )}

          {script.final_video && (
            <div className="flex flex-wrap gap-6">
              <div>
                <h4 className="mb-2 text-sm font-bold text-slate-700">🎉 ویدیوی نهایی</h4>
                <video
                  controls
                  src={script.final_video}
                  className="w-full max-w-md rounded-lg border border-slate-200"
                />
              </div>
              {script.final_video_voiced && (
                <div>
                  <h4 className="mb-2 text-sm font-bold text-slate-700">🔊 نسخه صداگذاری‌شده</h4>
                  <video
                    controls
                    src={script.final_video_voiced}
                    className="w-full max-w-md rounded-lg border border-violet-300"
                  />
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </Card>
  );
}
