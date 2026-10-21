import streamlit as st

def render_telemetry_tab(telemetry: dict):
    """Renders raw numerical readouts for all physical sub-systems."""
    st.subheader("Raw System Metrics & Telemetry Readouts")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Air Handling Unit 01 (AHU-01)")
        st.write(f"**Supply Fan Speed:** {telemetry['ahu']['fan_speed']:.1f} %")
        st.write(f"**Duct Differential Pressure:** {telemetry['ahu']['pressure']:.1f} Pa")
        st.write(f"**Air Flow Rate:** {telemetry['ahu']['cfm']:.0f} CFM")
        st.write(f"**Supply Air Temperature:** {telemetry['ahu']['supply_temp']:.1f} °C")
        st.write(f"**Fan Motor Power Draw:** {telemetry['ahu']['power_kw']:.2f} kW")

        st.markdown("---")

        st.markdown("#### Main Electrical Distribution Panel (MDB-01)")
        st.write(f"**3-Phase Line Voltage:** {telemetry['mdb']['voltage']:.1f} V")
        st.write(f"**Total Line Current:** {telemetry['mdb']['current']:.1f} A")
        st.write(f"**Power Factor (PF):** {telemetry['mdb']['pf']:.2f}")
        st.write(f"**Panel Active Power:** {telemetry['mdb']['power_kw']:.2f} kW")

    with col2:
        st.markdown("#### Basement Exhaust Fan (EF-02)")
        st.write(f"**CO Gas Concentration:** {telemetry['ef']['co_ppm']:.1f} PPM")
        st.write(f"**Exhaust Fan State:** {telemetry['ef']['status']}")
        st.write(f"**Motor Power Draw:** {telemetry['ef']['power_kw']:.2f} kW")

        st.markdown("---")

        st.markdown("#### Plumbing & Utility Pump (P-101)")
        st.write(f"**Tank Ultrasonic Level:** {telemetry['pump']['tank_level']:.1f} %")
        st.write(f"**Pump Operational Status:** {telemetry['pump']['status']}")
        st.write(f"**Motor Line Current:** {telemetry['pump']['current']:.1f} A")
        st.write(f"**Discharge Flow Rate:** {telemetry['pump']['flow_rate']:.1f} L/min")
        st.write(f"**Pump Power Draw:** {telemetry['pump']['power_kw']:.2f} kW")