"""Central module registry for dashboard navigation and routing."""

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class ModuleSpec:
    id: str
    label: str
    title: str
    academic_purpose: str


MODULE_SPECS: tuple[ModuleSpec, ...] = (
    ModuleSpec("m1", "M1 — PoW Monitor", "M1 — PROOF OF WORK MONITOR", "Network/block activity monitor"),
    ModuleSpec("m2", "M2 — Block Header", "M2 — BLOCK HEADER ANALYZER", "Block structure and consensus verification"),
    ModuleSpec("m3", "M3 — Difficulty History", "M3 — DIFFICULTY HISTORY", "Consensus adjustment time series"),
    ModuleSpec("m4", "M4 — Anomaly Detector", "M4 — AI COMPONENT: ANOMALY DETECTOR", "AI anomaly analysis on block activity"),
    ModuleSpec("m5", "M5 — Merkle Proof", "M5 — MERKLE PROOF VERIFIER", "Transaction inclusion proof"),
    ModuleSpec("m6", "M6 — Security Score", "M6 — SECURITY SCORE", "Economic/security risk model"),
    ModuleSpec("m7", "M7 — Difficulty Predictor", "M7 — DIFFICULTY PREDICTOR", "Second AI forecasting approach"),
)


def supported_module_specs(supported_ids: tuple[str, ...]) -> list[ModuleSpec]:
    """Return module specs in canonical order filtered by supported ids."""
    allowed = set(supported_ids)
    return [spec for spec in MODULE_SPECS if spec.id in allowed]


def module_by_label(label: str) -> ModuleSpec:
    """Return a module spec by its navigation label."""
    for spec in MODULE_SPECS:
        if spec.label == label:
            return spec
    raise KeyError(f"Unknown module label: {label}")


ModuleRenderer = Callable[[], None]
