# pages/1_AI_Diagnostics.py
import streamlit as st
from core.diagnostics import diagnose
from views.tab_diagnostics import render_diagnostics_tab

st.set_page_config(
    page_title="AI Diagnostics | EcoPulse AI",
    page_icon="🏭",
    layout="wide"
)

st.title("EcoPulse AI — Fault Intelligence & Optimization")
st.caption("Automated fault detection • Root-cause analysis • Predictive early warnings • Actionable energy savings")

# Get the latest data from the main app
telemetry = st.session_state.get("latest_telemetry")
history = st.session_state.get("telemetry_history")

if telemetry is None:
    st.warning("No live telemetry available yet. Please open the main dashboard first so the simulator can start collecting data.")
    st.stop()

# Run diagnostics
diagnostics = diagnose(telemetry, history)

# Render the full diagnostics UI
render_diagnostics_tab(diagnostics)