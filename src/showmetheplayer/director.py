from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from splot import fuse_json

DEFAULT_PROFILE = Path(__file__).resolve().parent / "profiles" / "player-director" / "profile.toml"


@dataclass(frozen=True)
class CameraMetric:
    camera_id: str
    player_visible: bool
    visibility: float
    occlusion: float
    sharpness: float
    face_angle: float
    available: bool = True
    observed_at: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CameraMetric:
        return cls(
            camera_id=str(data["camera_id"]),
            player_visible=bool(data.get("player_visible", False)),
            visibility=_score(data.get("visibility", 0)),
            occlusion=_score(data.get("occlusion", 1)),
            sharpness=_score(data.get("sharpness", 0)),
            face_angle=_score(data.get("face_angle", 0)),
            available=bool(data.get("available", True)),
            observed_at=data.get("observed_at"),
        )


def decide_from_payload(
    payload: dict[str, Any], *, profile: str | Path | None = None
) -> dict[str, Any]:
    metrics = [CameraMetric.from_dict(item) for item in payload.get("cameras") or []]
    return run_director(
        metrics,
        state=payload.get("state") or {},
        profile=profile,
        now=payload.get("now"),
    )


def run_director(
    metrics: list[CameraMetric],
    *,
    state: dict[str, Any] | None = None,
    profile: str | Path | None = None,
    now: str | None = None,
) -> dict[str, Any]:
    if not metrics:
        raise ValueError("at least one camera metric is required")
    request: dict[str, Any] = {
        "profile": str(Path(profile or DEFAULT_PROFILE).resolve()),
        "candidates": metrics_to_candidates(metrics),
        "state": state or {},
        "include_evaluations": True,
    }
    if now is not None:
        request["now"] = now
    return fuse_json(request)


def metrics_to_candidates(metrics: list[CameraMetric]) -> list[dict[str, Any]]:
    return [metric_to_candidate(metric) for metric in metrics]


def metric_to_candidate(metric: CameraMetric) -> dict[str, Any]:
    return {
        "id": metric.camera_id,
        "kind": "camera_view",
        "source_ids": [metric.camera_id],
        "payload": {
            "player_visible": metric.player_visible,
            "visibility": metric.visibility if metric.player_visible else 0.0,
            "occlusion": metric.occlusion,
            "sharpness": metric.sharpness,
            "face_angle": metric.face_angle,
            "available": metric.available,
        },
        "metadata": {
            "observed_at": metric.observed_at,
        },
    }


def build_switch_command(result: dict[str, Any]) -> dict[str, Any]:
    decision = result.get("decision")
    if not isinstance(decision, dict):
        raise TypeError("Splot result is missing a decision object")
    camera_id = decision.get("selected_candidate_id")
    status = str(decision.get("status") or "")
    if status == "kept_previous" and camera_id:
        action = "keep"
    elif status in {"selected", "routed"} and camera_id:
        action = "switch"
    elif status == "fallback":
        action = "fallback"
    else:
        action = "wait"
    return {
        "action": action,
        "camera_id": camera_id,
        "decision_id": decision.get("id"),
        "status": status,
        "confidence": float(decision.get("confidence") or 0),
        "reason": decision.get("policy_reason"),
    }


def _score(value: Any) -> float:
    return max(0.0, min(1.0, float(value)))
