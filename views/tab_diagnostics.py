# views/tab_diagnostics.py
import streamlit as st
import pandas as pd
from core.diagnostics import Diagnostic
from datetime import datetime

def render_diagnostics_tab(diagnostics: list[Diagnostic]):
    st.subheader("🧠 AI Fault Intelligence")

    if not diagnostics:
        st.success("✅ No active faults detected. All systems operating within normal parameters.")
        st.info("The diagnostic engine runs after every telemetry cycle and applies both rule-based and statistical checks.")
        return

    # Summary metrics
    critical = sum(1 for d in diagnostics if d.severity == "CRITICAL")
    high     = sum(1 for d in diagnostics if d.severity == "HIGH")
    total_extra_kw = sum(d.energy_impact_kw for d in diagnostics)
    total_cost     = sum(d.energy_impact_inr_per_day for d in diagnostics)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Active Faults", len(diagnostics))
    c2.metric("Critical / High", f"{critical} / {high}")
    c3.metric("Est. Extra Power", f"{total_extra_kw:.1f} kW")
    c4.metric("Est. Daily Cost Impact", f"₹{total_cost:,.0f}")

    st.markdown("---")

    for d in diagnostics:
        color = {
            "CRITICAL": "🔴",
            "HIGH": "🟠",
            "MEDIUM": "🟡",
            "LOW": "🔵",
            "INFO": "⚪"
        }.get(d.severity, "⚪")

        with st.expander(f"{color} **{d.equipment}** — {d.title}  |  Confidence: {d.confidence:.0%}", expanded=(d.severity in ["CRITICAL", "HIGH"])):
            st.markdown(f"**Severity:** `{d.severity}`")
            st.write(d.description)

            st.markdown("**Probable Causes (ranked)**")
            for cause in d.probable_causes:
                st.write(f"- {cause['cause']}  *(confidence {cause['confidence']:.0%})*")

            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Extra Power", f"{d.energy_impact_kw:.1f} kW")
            with col_b:
                st.metric("Est. Cost / Day", f"₹{d.energy_impact_inr_per_day:,.0f}")

            st.markdown("**Recommended Actions**")
            for i, action in enumerate(d.recommended_actions, 1):
                st.write(f"{i}. {action}")

            st.caption(f"Responsible team → **{d.responsible_team}**")

    # Downloadable report
    st.markdown("---")
    st.subheader("📄 Generate Diagnostic Report")

    report_md = _build_markdown_report(diagnostics)
    st.download_button(
        label="⬇️ Download Full Diagnostic Report (.md)",
        data=report_md,
        file_name=f"EcoPulse_Diagnostic_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
        mime="text/markdown"
    )


def _build_markdown_report(diagnostics: list[Diagnostic]) -> str:
    lines = [
        "# EcoPulse-AI – Automated Diagnostic Report",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        f"**Total Active Faults:** {len(diagnostics)}",
        "",
        "---",
        ""
    ]

    for d in diagnostics:
        lines.extend([
            f"## {d.equipment} – {d.title}",
            f"**Severity:** {d.severity}  |  **Confidence:** {d.confidence:.0%}",
            "",
            d.description,
            "",
            "### Probable Causes",
        ])
        for c in d.probable_causes:
            lines.append(f"- {c['cause']} (confidence {c['confidence']:.0%})")

        lines.extend([
            "",
            f"**Estimated Extra Power:** {d.energy_impact_kw:.1f} kW",
            f"**Estimated Daily Cost Impact:** ₹{d.energy_impact_inr_per_day:,.0f}",
            "",
            "### Recommended Actions",
        ])
        for i, a in enumerate(d.recommended_actions, 1):
            lines.append(f"{i}. {a}")

        lines.extend([
            "",
            f"**Responsible Team:** {d.responsible_team}",
            "",
            "---",
            ""
        ])

    return "\n".join(lines)