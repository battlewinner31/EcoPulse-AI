# core/diagnostics.py
from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
import config


@dataclass
class Diagnostic:
    equipment: str
    severity: str                    # CRITICAL | HIGH | MEDIUM | EARLY WARNING | LOW | INFO
    title: str
    description: str
    probable_causes: List[Dict[str, Any]]
    energy_impact_kw: float
    energy_impact_inr_per_day: float
    recommended_actions: List[str]
    responsible_team: str
    confidence: float

    # Phase 3 – Optimization
    optimization_suggestions: List[str] = field(default_factory=list)
    estimated_savings_kw: float = 0.0
    estimated_savings_inr_per_day: float = 0.0
    estimated_savings_inr_per_month: float = 0.0

    def to_dict(self):
        return asdict(self)


def _estimate_cost(extra_kw: float, hours: float = 24.0, rate: float = 8.0) -> float:
    return round(extra_kw * hours * rate, 0)


def _linear_slope(series: pd.Series) -> Optional[float]:
    if len(series) < 15:
        return None
    y = series.values.astype(float)
    x = np.arange(len(y))
    slope = np.polyfit(x, y, 1)[0]
    return float(slope)


def diagnose(telemetry: dict, history: pd.DataFrame | None = None) -> List[Diagnostic]:
    results: List[Diagnostic] = []

    ahu = telemetry["ahu"]
    ef = telemetry["ef"]
    mdb = telemetry["mdb"]
    pump = telemetry["pump"]

    # ------------------------------------------------------------------
    # HARD FAULTS (Phase 1)
    # ------------------------------------------------------------------

    # 1. AHU-01
    if ahu["pressure"] > 250 or ahu["fan_speed"] > 85 or ahu["power_kw"] > 18:
        extra_kw = max(0.0, ahu["power_kw"] - config.BASE_AHU_NOMINAL_KW)
        savings_kw = extra_kw * 0.85          # realistic recovery after fixing filters/dampers
        results.append(Diagnostic(
            equipment="AHU-01",
            severity="HIGH",
            title="Elevated Duct Static Pressure / Fan Overload",
            description=(
                f"Duct differential pressure is {ahu['pressure']:.0f} Pa "
                f"(normal ~120 Pa). Fan running at {ahu['fan_speed']:.0f}% "
                f"and drawing {ahu['power_kw']:.1f} kW."
            ),
            probable_causes=[
                {"cause": "Clogged or dirty filters / coils", "confidence": 0.75},
                {"cause": "Damper stuck closed or partially closed", "confidence": 0.55},
                {"cause": "Duct collapse or excessive resistance", "confidence": 0.40},
            ],
            energy_impact_kw=round(extra_kw, 1),
            energy_impact_inr_per_day=_estimate_cost(extra_kw),
            recommended_actions=[
                "Inspect and replace AHU filters immediately",
                "Check all volume control dampers for proper position",
                "Measure static pressure at multiple points to locate restriction",
                "Schedule coil cleaning if pressure remains high after filter change",
            ],
            responsible_team="HVAC / Mechanical Maintenance",
            confidence=0.88,
            # Phase 3
            optimization_suggestions=[
                "Replace filters and clean coils → expect fan power to drop to ~11–12 kW",
                "Verify VAV / damper positions are not forcing high static",
                "Consider enabling static-pressure reset strategy once system is healthy",
            ],
            estimated_savings_kw=round(savings_kw, 1),
            estimated_savings_inr_per_day=_estimate_cost(savings_kw),
            estimated_savings_inr_per_month=_estimate_cost(savings_kw) * 30
        ))

    # 2. EF-02
    if ef["co_ppm"] > 25 or ef["power_kw"] > 8:
        extra_kw = max(0.0, ef["power_kw"] - config.BASE_EF_LOW_KW)
        savings_kw = extra_kw * 0.90
        results.append(Diagnostic(
            equipment="EF-02",
            severity="CRITICAL" if ef["co_ppm"] > 35 else "HIGH",
            title="Elevated Carbon Monoxide – Exhaust Fan in High-Purge Mode",
            description=(
                f"CO sensor reading {ef['co_ppm']:.1f} ppm "
                f"(safe threshold typically < 25–30 ppm). "
                f"Fan power {ef['power_kw']:.1f} kW (normal ~2.8 kW)."
            ),
            probable_causes=[
                {"cause": "Vehicle exhaust accumulation in basement / parking", "confidence": 0.70},
                {"cause": "Blocked exhaust duct or discharge louvre", "confidence": 0.50},
                {"cause": "CO sensor drift / calibration issue", "confidence": 0.30},
            ],
            energy_impact_kw=round(extra_kw, 1),
            energy_impact_inr_per_day=_estimate_cost(extra_kw),
            recommended_actions=[
                "Immediately verify CO levels with handheld meter",
                "Inspect basement for idling vehicles or gas leaks",
                "Check exhaust ductwork and discharge points for blockages",
                "Calibrate CO sensor if readings appear inconsistent",
            ],
            responsible_team="HVAC + Safety / Facilities",
            confidence=0.90,
            optimization_suggestions=[
                "Clear any blockage and return fan to demand-controlled ventilation",
                "Implement CO-based fan speed control instead of continuous high-purge",
                "Expected power reduction to ~2.8–3.5 kW under normal conditions",
            ],
            estimated_savings_kw=round(savings_kw, 1),
            estimated_savings_inr_per_day=_estimate_cost(savings_kw),
            estimated_savings_inr_per_month=_estimate_cost(savings_kw) * 30
        ))

    # 3. MDB-01
    if mdb["pf"] < 0.85:
        extra_kw = mdb["power_kw"] * (0.95 - mdb["pf"]) * 0.4
        savings_kw = extra_kw * 0.80
        results.append(Diagnostic(
            equipment="MDB-01",
            severity="MEDIUM" if mdb["pf"] > 0.80 else "HIGH",
            title="Degraded Power Factor",
            description=(
                f"Power factor has dropped to {mdb['pf']:.2f} "
                f"(target ≥ 0.95). Line current elevated."
            ),
            probable_causes=[
                {"cause": "Failed or offline power factor correction capacitors", "confidence": 0.80},
                {"cause": "Large inductive loads running without compensation", "confidence": 0.55},
                {"cause": "Harmonic distortion from VFDs / non-linear loads", "confidence": 0.35},
            ],
            energy_impact_kw=round(extra_kw, 1),
            energy_impact_inr_per_day=_estimate_cost(extra_kw),
            recommended_actions=[
                "Inspect capacitor bank and contactors",
                "Measure individual phase currents and harmonics",
                "Engage electrical team to restore PF correction",
                "Review utility bill for PF penalty charges",
            ],
            responsible_team="Electrical Maintenance",
            confidence=0.85,
            optimization_suggestions=[
                "Restore / replace PFC capacitor banks to bring PF ≥ 0.95",
                "Expected reduction in line losses and possible utility penalty avoidance",
                "Consider automatic PF controller if not already present",
            ],
            estimated_savings_kw=round(savings_kw, 1),
            estimated_savings_inr_per_day=_estimate_cost(savings_kw),
            estimated_savings_inr_per_month=_estimate_cost(savings_kw) * 30
        ))

    # 4. P-101
    if pump["flow_rate"] < 40 or pump["tank_level"] < 25 or pump["current"] < 8:
        # Cavitation often reduces power but wastes the process – savings come after fix
        savings_kw = 1.5   # conservative estimate once pump is running efficiently again
        results.append(Diagnostic(
            equipment="P-101",
            severity="HIGH",
            title="Pump Cavitation / Suction-Side Problem Suspected",
            description=(
                f"Discharge flow {pump['flow_rate']:.0f} L/min "
                f"(normal ~120 L/min). Motor current {pump['current']:.1f} A "
                f"(normal ~14 A). Tank level {pump['tank_level']:.0f}%."
            ),
            probable_causes=[
                {"cause": "Low suction tank level / NPSH insufficient", "confidence": 0.75},
                {"cause": "Clogged suction strainer or partially closed suction valve", "confidence": 0.65},
                {"cause": "Air leak on suction line", "confidence": 0.40},
                {"cause": "Pump impeller wear or damage", "confidence": 0.25},
            ],
            energy_impact_kw=round(config.BASE_PUMP_NOMINAL_KW - pump["power_kw"], 1),
            energy_impact_inr_per_day=0,
            recommended_actions=[
                "Check suction tank level and fill if low",
                "Inspect and clean suction strainer",
                "Verify all suction-side valves are fully open",
                "Listen for cavitation noise and check for air leaks",
                "If persistent, schedule pump performance test",
            ],
            responsible_team="Plumbing / Mechanical",
            confidence=0.87,
            optimization_suggestions=[
                "Restore proper NPSH and clear suction path → pump returns to efficient operating point",
                "Expected power ~4.3–4.6 kW at design flow once cavitation is eliminated",
                "Consider adding low-level interlock to prevent future dry-run / cavitation",
            ],
            estimated_savings_kw=round(savings_kw, 1),
            estimated_savings_inr_per_day=_estimate_cost(savings_kw),
            estimated_savings_inr_per_month=_estimate_cost(savings_kw) * 30
        ))

    # ------------------------------------------------------------------
    # PREDICTIVE / EARLY WARNINGS (Phase 2)
    # ------------------------------------------------------------------
    if history is not None and len(history) >= 40:

        ahu_slope = _linear_slope(history["AHU_kW"].tail(60))
        if ahu_slope is not None and ahu_slope > 0.015:
            already_faulted = any(
                d.equipment == "AHU-01" and d.severity in ["HIGH", "CRITICAL"]
                for d in results
            )
            if not already_faulted:
                projected_extra = ahu_slope * 60 * 15   # 15-min projection
                savings_kw = projected_extra * 0.7
                results.append(Diagnostic(
                    equipment="AHU-01",
                    severity="EARLY WARNING",
                    title="Gradual AHU Power Increase Detected",
                    description=(
                        f"AHU power is rising at approximately {ahu_slope * 60:.2f} kW per minute. "
                        "This pattern typically precedes filter loading or increasing duct resistance."
                    ),
                    probable_causes=[
                        {"cause": "Progressive filter loading", "confidence": 0.70},
                        {"cause": "Slowly closing damper or developing restriction", "confidence": 0.45},
                    ],
                    energy_impact_kw=round(projected_extra, 1),
                    energy_impact_inr_per_day=_estimate_cost(projected_extra),
                    recommended_actions=[
                        "Schedule filter inspection within the next 24–48 hours",
                        "Monitor static pressure trend closely",
                        "Check differential pressure across filters if sensors are available",
                    ],
                    responsible_team="HVAC / Mechanical Maintenance",
                    confidence=0.75,
                    optimization_suggestions=[
                        "Proactive filter change now can avoid a full high-static event",
                        "Estimated prevention of 8–12 kW continuous extra load",
                    ],
                    estimated_savings_kw=round(savings_kw, 1),
                    estimated_savings_inr_per_day=_estimate_cost(savings_kw),
                    estimated_savings_inr_per_month=_estimate_cost(savings_kw) * 30
                ))

        pf_slope = _linear_slope(history["Power_Factor"].tail(60))
        if pf_slope is not None and pf_slope < -0.0008:
            already_faulted = any(
                d.equipment == "MDB-01" and d.severity in ["HIGH", "CRITICAL"]
                for d in results
            )
            if not already_faulted:
                results.append(Diagnostic(
                    equipment="MDB-01",
                    severity="EARLY WARNING",
                    title="Gradual Power Factor Decline",
                    description=(
                        f"Power factor is trending downward "
                        f"(slope ≈ {pf_slope * 60:.4f} per minute). "
                        "This often indicates capacitor bank degradation or increasing inductive load."
                    ),
                    probable_causes=[
                        {"cause": "Aging or failing PFC capacitors", "confidence": 0.65},
                        {"cause": "Increasing inductive load without compensation", "confidence": 0.40},
                    ],
                    energy_impact_kw=0.8,
                    energy_impact_inr_per_day=_estimate_cost(0.8),
                    recommended_actions=[
                        "Inspect capacitor bank health",
                        "Review recent load changes",
                        "Plan preventive maintenance on PFC equipment",
                    ],
                    responsible_team="Electrical Maintenance",
                    confidence=0.70,
                    optimization_suggestions=[
                        "Preventive capacitor maintenance can avoid future PF penalties and extra losses",
                        "Target PF ≥ 0.95 for optimal efficiency",
                    ],
                    estimated_savings_kw=0.6,
                    estimated_savings_inr_per_day=_estimate_cost(0.6),
                    estimated_savings_inr_per_month=_estimate_cost(0.6) * 30
                ))

    # Sort by severity
    severity_order = {
        "CRITICAL": 0,
        "HIGH": 1,
        "MEDIUM": 2,
        "EARLY WARNING": 3,
        "LOW": 4,
        "INFO": 5
    }
    results.sort(key=lambda d: severity_order.get(d.severity, 99))

    return results