import streamlit as st
import pandas as pd
from core.diagnostics import diagnose
from views.tab_diagnostics import render_diagnostics_tab   # we already created this

st.set_page_config(
    page_title="AI Diagnostics | EcoPulse-AI",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 AI Fault Intelligence")
st.caption("Automated fault detection • Root-cause analysis • Energy impact • Actionable recommendations")

# ------------------------------------------------------------------
# Get the latest data from the main app (shared via session_state)
# ------------------------------------------------------------------
telemetry = st.session_state.get("latest_telemetry")
history = st.session_state.get("telemetry_history")

if telemetry is None:
    st.warning("No live telemetry available yet. Please open the main dashboard first so the simulator can start collecting data.")
    st.stop()

# Run diagnostics (or use cached result if you prefer)
diagnostics = diagnose(telemetry, history)

# Render the full diagnostics UI
render_diagnostics_tab(diagnostics)