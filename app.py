# app.py
import time
import pandas as pd
import streamlit as st

from components.metrics import render_kpis
from components.sidebar import render_sidebar
from core.logger import initialize_session_state, record_telemetry_event
from core.physics import simulate_ahu, simulate_ef, simulate_mdb, simulate_pump
from core.diagnostics import diagnose
from views.tab_analytics import render_analytics_tab
from views.tab_logbook import render_logbook_tab
from views.tab_telemetry import render_telemetry_tab
from views.tab_diagnostics import render_diagnostics_tab

# -------------------------------------------------
# Page Config
# -------------------------------------------------
st.set_page_config(
    page_title="EcoPulse AI | Virtual Building Management System",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------
# Branding Header
# -------------------------------------------------
st.title("EcoPulse AI")
st.caption("Intelligent Virtual Building Management System  •  Predictive Diagnostics  •  Energy Optimization")
st.markdown("---")

# -------------------------------------------------
# Initialize + Controls
# -------------------------------------------------
initialize_session_state()
controls = render_sidebar()

# -------------------------------------------------
# Physics Simulation
# -------------------------------------------------
now_str = pd.Timestamp.now().strftime('%H:%M:%S')

ahu_data = simulate_ahu(controls['sim_ahu_resistance'], controls['outdoor_temp'])
ef_data  = simulate_ef(controls['sim_co_shift'])
mdb_data = simulate_mdb(controls['sim_pf_drop'], ahu_data['power_kw'], ef_data['power_kw'])
pump_data = simulate_pump(controls['sim_pump_cavitation'])

telemetry = {
    "ahu": ahu_data,
    "ef": ef_data,
    "mdb": mdb_data,
    "pump": pump_data
}

# -------------------------------------------------
# Logging
# -------------------------------------------------
record_telemetry_event(now_str, telemetry)
st.session_state["latest_telemetry"] = telemetry

# -------------------------------------------------
# KPIs
# -------------------------------------------------
render_kpis(telemetry, controls['outdoor_temp'])

# -------------------------------------------------
# Main Tabs (Everything on one page)
# -------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "Live Telemetry",
    "Event Log",
    "Trend Analysis",
    "AI Diagnostics"
])

with tab1:
    render_telemetry_tab(telemetry)

with tab2:
    render_logbook_tab()

with tab3:
    render_analytics_tab()

with tab4:
    # Clean separator for the AI section
    st.markdown("### AI Fault Intelligence & Optimization")
    st.caption("Real-time fault detection • Predictive early warnings • Actionable energy savings")
    
    history = st.session_state.get("telemetry_history")
    diagnostics = diagnose(telemetry, history)
    render_diagnostics_tab(diagnostics)

# -------------------------------------------------
# Auto-refresh
# -------------------------------------------------
time.sleep(1)
st.rerun()