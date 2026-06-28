from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from splot import RoundResult, SplotState, builtin_registry, run_round


DEFAULT_PROFILE = Path(__file__).resolve().parent / "profiles" / "player-director"


@dataclass
class CameraMetric:
    camera_id: str
    player_visible: bool
    visibility: float
    tracking_confidence: float
    occlusion: float
    sharpness: float
    face_angle: float
    latency_ms: int
    available: bool = True
    observed_at: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CameraMetric":
        return cls(
            camera_id=str(data["camera_id"]),
            player_visible=bool(data.get("player_visible", False)),
            visibility=_score(data.get("visibility", 0)),
            tracking_confidence=_score(data.get("tracking_confidence", 0)),
            occlusion=_score(data.get("occlusion", 1)),
            sharpness=_score(data.get("sharpness", 0)),
            face_angle=_score(data.get("face_angle", 0)),
            latency_ms=max(0, int(data.get("latency_ms", 1000))),
            available=bool(data.get("available", True)),
            observed_at=data.get("observed_at"),
        )


def decide_from_payload(payload: dict[str, Any], *, profile: str | Path | None = None) -> RoundResult:
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
    state: dict[str, Any] | SplotState | None = None,
    profile: str | Path | None = None,
    now: str | None = None,
) -> RoundResult:
    observations = [
        {
            "id": "camera_metrics",
            "kind": "camera_metrics",
            "observed_at": now,
            "values": {"camera_count": len(metrics)},
        }
    ]
    return run_round(
        profile=profile or DEFAULT_PROFILE,
        observations=observations,
        candidates=metrics_to_candidates(metrics),
        previous_state=state or {},
        registry=builtin_registry(),
        now=now,
    )


def metrics_to_candidates(metrics: list[CameraMetric]) -> list[dict[str, Any]]:
    return [metric_to_candidate(metric) for metric in metrics]


def metric_to_candidate(metric: CameraMetric) -> dict[str, Any]:
    latency = min(metric.latency_ms / 1000.0, 1.0)
    return {
        "id": metric.camera_id,
        "kind": "camera_view",
        "source_ids": [metric.camera_id],
        "payload": {
            "player_visible": metric.player_visible,
            "visibility": metric.visibility,
            "tracking_confidence": metric.tracking_confidence,
            "occlusion": metric.occlusion,
            "sharpness": metric.sharpness,
            "face_angle": metric.face_angle,
            "latency": latency,
            "available": metric.available,
        },
        "metadata": {
            "observed_at": metric.observed_at,
            "latency_ms": metric.latency_ms,
        },
    }


def build_switch_command(result: RoundResult) -> dict[str, Any]:
    decision = result.decision
    camera_id = decision.selected_candidate_id
    if decision.status == "kept_previous" and camera_id:
        action = "keep"
    elif decision.status in {"selected", "routed"} and camera_id:
        action = "switch"
    elif decision.status == "fallback":
        action = "fallback"
    else:
        action = "wait"
    return {
        "action": action,
        "camera_id": camera_id,
        "decision_id": decision.id,
        "status": decision.status,
        "confidence": decision.confidence,
        "reason": decision.policy_reason,
    }


def _score(value: Any) -> float:
    return max(0.0, min(1.0, float(value)))
