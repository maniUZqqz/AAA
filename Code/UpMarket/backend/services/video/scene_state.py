"""Continuity between five-second segments, beyond the last frame.

Wan 2.2 continues from an image. That image carries everything visible in one
frame and nothing else, which is why stitched videos drift: the jacket was blue
in segment one and the last frame happened to show the sleeve, so segment two
invents a colour. The light was warm and low; the frame shows a wall; segment
three lights it from the front.

So each segment records what the scene *is*, not only what it looked like at
the final instant, and the next segment's prompt is built from both.

Everything here is plain data. There is no model call: the state comes from the
script the LLM already wrote (§9.1) and from the previous segment's own state,
so carrying continuity costs nothing extra per segment. Vision-derived state —
reading the rendered frame to check the jacket really is still blue — belongs
to phase 21's QC, which will write into these same fields.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field

#: The axes that visibly break when they are not carried forward. Kept short on
#: purpose: every field is one more thing in the prompt, and a prompt stuffed
#: with fifty attributes describes nothing.
FIELDS = (
    "characters",
    "objects",
    "location",
    "lighting",
    "camera",
    "clothing",
    "colors",
    "action",
)


@dataclass
class SceneState:
    """What the scene contains, so the next segment does not re-invent it."""

    characters: list[str] = field(default_factory=list)
    objects: list[str] = field(default_factory=list)
    location: str = ""
    lighting: str = ""
    camera: str = ""
    clothing: list[str] = field(default_factory=list)
    colors: list[str] = field(default_factory=list)
    #: The only field that is *meant* to change between segments; everything
    #: else changing is usually drift.
    action: str = ""

    def as_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict | None) -> SceneState:
        """Build from stored JSON, ignoring anything we do not know.

        Tolerant by design: old segment rows have no state at all, and a
        renamed field must not break a resume of a job that is half done.
        """
        data = data or {}
        known = {}
        for name in FIELDS:
            value = data.get(name)
            if value is None:
                continue
            default = getattr(cls(), name)
            if isinstance(default, list):
                known[name] = [str(v) for v in value] if isinstance(value, list) else [str(value)]
            else:
                known[name] = str(value)
        return cls(**known)

    @property
    def is_empty(self) -> bool:
        return not any(getattr(self, name) for name in FIELDS)

    def carry_forward(self, action: str = "") -> SceneState:
        """The state the next segment starts from.

        Everything persists except the action — which is exactly the point.
        """
        nxt = SceneState.from_dict(self.as_dict())
        nxt.action = action
        return nxt

    def continuity_prompt(self) -> str:
        """The sentence appended to the next segment's visual prompt.

        Phrased as constraints rather than description ("the same X"), because
        a plain restatement reads to the model as a new subject to introduce,
        and it will happily introduce a second person wearing the same coat.
        """
        parts = []
        if self.characters:
            parts.append("the same " + ", ".join(self.characters))
        if self.clothing:
            parts.append("still wearing " + ", ".join(self.clothing))
        if self.objects:
            parts.append("the same " + ", ".join(self.objects))
        if self.location:
            parts.append(f"in the same {self.location}")
        if self.lighting:
            parts.append(f"unchanged lighting: {self.lighting}")
        if self.camera:
            parts.append(f"camera: {self.camera}")
        if self.colors:
            parts.append("consistent colours: " + ", ".join(self.colors))
        if not parts:
            return ""
        return "Continuity — " + "; ".join(parts) + "."


def from_scene(scene, previous: SceneState | None = None) -> SceneState:
    """State for a scene, inheriting whatever the previous segment established.

    The script's own fields win where it says something; the previous state
    fills the rest. A scene that says nothing about clothing means "as before",
    not "no clothing" — and treating silence as a reset is precisely the drift
    this module exists to stop.
    """
    base = previous.carry_forward() if previous else SceneState()
    declared = SceneState.from_dict((getattr(scene, "state", None) or {}))

    for name in FIELDS:
        value = getattr(declared, name)
        if value:
            setattr(base, name, value)

    # A new visual anchor is a deliberate cut; nothing should be carried over.
    transition = getattr(scene, "transition", None)
    if transition == "NEW_SCENE":
        base = declared

    base.action = (
        declared.action
        or getattr(scene, "motion_prompt", "")
        or ""
    )
    return base


def build_prompt(scene, state: SceneState) -> str:
    """The full positive prompt for one segment: its own text plus continuity."""
    prompt = (getattr(scene, "visual_prompt", "") or "").strip()
    motion = (getattr(scene, "motion_prompt", "") or "").strip()
    if motion:
        prompt = f"{prompt}. Motion: {motion}" if prompt else f"Motion: {motion}"

    continuity = state.continuity_prompt() if state else ""
    if continuity and getattr(scene, "transition", None) != "NEW_SCENE":
        prompt = f"{prompt} {continuity}".strip()
    return prompt
