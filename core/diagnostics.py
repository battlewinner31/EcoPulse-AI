# core/diagnostics.py
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import List, Dict, Any
import pandas as pd
import config

@dataclass
class Diagnostic:
    equipment: str
    severity: str                    # CRITICAL | HIGH | MEDIUM | LOW | INFO
    title: str
    description: str
    probable_causes: List[Dict[str, Any]]   # [{"cause": "...", "confidence": 0.85}, ...]
    energy_impact_kw: float          # estimated extra power
    energy_impact_inr_per_day: float # rough cost (assume ₹8/kWh)
    recommended_actions: List[str]
    responsible_team: str
    confidence: float                # overall confidence 0–1

    def to_dict(self):
        return asdict(self)


def _estimate_cost(extra_kw: float, hours: float = 24.0, rate: float = 8.0) -> float:
    return round(extra_kw * hours * rate, 0)


def diagnose(telemetry: dict, history: pd.DataFrame | None = None) -> List[Diagnostic]:
    """
    Main entry point. Call after every telemetry cycle.
    Returns a list of Diagnostic objects (empty list = all healthy).
    """
    results: List[Diagnostic] = []

    ahu = telemetry["ahu"]
    ef  = telemetry["ef"]
    mdb = telemetry["mdb"]
    pump = telemetry["pump"]

    # ------------------------------------------------------------------
    # 1. AHU-01 – Duct Resistance / High Static Pressure
    # ------------------------------------------------------------------
    if ahu["pressure"] > 250 or ahu["fan_speed"] > 85 or ahu["power_kw"] > 18:
        extra_kw = ahu["power_kw"] - config.BASE_AHU_NOMINAL_KW
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
            confidence=0.88
        ))

    # ------------------------------------------------------------------
    # 2. EF-02 – High CO / Continuous Purge Mode
    # ------------------------------------------------------------------
    if ef["co_ppm"] > 25 or ef["power_kw"] > 8:
        extra_kw = ef["power_kw"] - config.BASE_EF_LOW_KW
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
            confidence=0.90
        ))

    # ------------------------------------------------------------------
    # 3. MDB-01 – Power Factor Drop
    # ------------------------------------------------------------------
    if mdb["pf"] < 0.85:
        # rough estimate of reactive power penalty / extra losses
        extra_kw = mdb["power_kw"] * (0.95 - mdb["pf"]) * 0.4   # simplified
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
            confidence=0.85
        ))

    # ------------------------------------------------------------------
    # 4. P-101 – Cavitation / Low Flow + Low Current
    # ------------------------------------------------------------------
    if pump["flow_rate"] < 40 or pump["tank_level"] < 25 or pump["current"] < 8:
        # note: cavitation usually shows lower current + low flow
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
            energy_impact_kw=round(config.BASE_PUMP_NOMINAL_KW - pump["power_kw"], 1),  # often lower power
            energy_impact_inr_per_day=0,   # energy may actually drop, but process impact is high
            recommended_actions=[
                "Check suction tank level and fill if low",
                "Inspect and clean suction strainer",
                "Verify all suction-side valves are fully open",
                "Listen for cavitation noise and check for air leaks",
                "If persistent, schedule pump performance test",
            ],
            responsible_team="Plumbing / Mechanical",
            confidence=0.87
        ))

    # ------------------------------------------------------------------
    # 5. Generic statistical checks (using recent history)
    # ------------------------------------------------------------------
    if history is not None and len(history) >= 10:
        recent = history.tail(15)

        # Sudden AHU power spike
        if recent["AHU_kW"].iloc[-1] > recent["AHU_kW"].mean() * 1.6:
            results.append(Diagnostic(
                equipment="AHU-01",
                severity="MEDIUM",
                title="Sudden AHU Power Spike Detected",
                description="AHU power has risen sharply compared with the recent baseline.",
                probable_causes=[
                    {"cause": "Filter loading or damper change", "confidence": 0.60},
                    {"cause": "VFD or control issue", "confidence": 0.35},
                ],
                energy_impact_kw=round(recent["AHU_kW"].iloc[-1] - recent["AHU_kW"].mean(), 1),
                energy_impact_inr_per_day=_estimate_cost(recent["AHU_kW"].iloc[-1] - recent["AHU_kW"].mean()),
                recommended_actions=["Review AHU trend chart", "Check recent control changes"],
                responsible_team="HVAC",
                confidence=0.70
            ))

        # Sustained low PF
        if recent["Power_Factor"].mean() < 0.88:
            # already covered by rule above, but can reinforce
            pass

    # Sort by severity (CRITICAL first)
    severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
    results.sort(key=lambda d: severity_order.get(d.severity, 99))

    return results