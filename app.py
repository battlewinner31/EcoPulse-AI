# app.py
import time
import pandas as pd
import streamlit as st

from components.metrics import render_kpis
from components.sidebar import render_sidebar
from core.logger import initialize_session_state, record_telemetry_event
from core.physics import simulate_ahu, simulate_ef, simulate_mdb, simulate_pump
from views.tab_analytics import render_analytics_tab
from views.tab_logbook import render_logbook_tab
from views.tab_telemetry import render_telemetry_tab

# -------------------------------------------------
# Page Configuration
# -------------------------------------------------
st.set_page_config(
    page_title="EcoPulse-AI | Virtual BMS",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------
# 1. Initialize Log Tables in State
# -------------------------------------------------
initialize_session_state()

# -------------------------------------------------
# 2. Render Sidebar & Gather Input Controls
# -------------------------------------------------
controls = render_sidebar()

# -------------------------------------------------
# 3. Execute Physics Calculations
# -------------------------------------------------
now_str = pd.Timestamp.now().strftime('%H:%M:%S')

ahu_data = simulate_ahu(controls['sim_ahu_resistance'], controls['outdoor_temp'])
ef_data = simulate_ef(controls['sim_co_shift'])
mdb_data = simulate_mdb(controls['sim_pf_drop'], ahu_data['power_kw'], ef_data['power_kw'])
pump_data = simulate_pump(controls['sim_pump_cavitation'])

telemetry = {
    'ahu': ahu_data,
    'ef': ef_data,
    'mdb': mdb_data,
    'pump': pump_data
}

# -------------------------------------------------
# 4. Log Raw Telemetry Values
# -------------------------------------------------
record_telemetry_event(now_str, telemetry)

# -------------------------------------------------
# 5. Share latest data with the AI Diagnostics page
# -------------------------------------------------
st.session_state["latest_telemetry"] = telemetry
# (telemetry_history is already maintained inside logger.py)

# -------------------------------------------------
# 6. Render Header & KPI Cards
# -------------------------------------------------
render_kpis(telemetry, controls['outdoor_temp'])

# -------------------------------------------------
# 7. Render the original 3 tabs only
# -------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "📊 Live Telemetry Overview",
    "📜 Chronological Event Log",
    "📈 Trend Analysis"
])

with tab1:
    render_telemetry_tab(telemetry)

with tab2:
    render_logbook_tab()

with tab3:
    render_analytics_tab()

# -------------------------------------------------
# 8. Polling Interval Tick
# -------------------------------------------------
time.sleep(1)
st.rerun()