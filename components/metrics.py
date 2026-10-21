import streamlit as st

def render_kpis(telemetry: dict, outdoor_temp: float):
    """Renders top header and KPI summary cards."""
    st.title("🏭 Building Management System — Telemetry Console")

    st.markdown(
        '<div style="background-color: #1A2634; color: #00D1B2; padding: 12px; border-radius: 6px; text-align: center; font-weight: 600; font-size: 18px; border: 1px solid #233548; margin-bottom: 20px;">'
        'SYSTEM MONITORING ACTIVE — UNFILTERED TELEMETRY STREAM'
        '</div>',
        unsafe_allow_html=True
    )

    total_kw = telemetry['mdb']['power_kw'] + telemetry['pump']['power_kw']

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Active Load", f"{total_kw:.1f} kW")
    m2.metric("Overall Power Factor", f"{telemetry['mdb']['pf']:.2f}")
    m3.metric("Outdoor Ambient Temp", f"{outdoor_temp:.1f} °C")
    m4.metric("Polled Telemetry Logs", f"{len(st.session_state.event_log)} Logs")

    st.markdown("---")