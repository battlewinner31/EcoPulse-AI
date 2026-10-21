import pandas as pd
import streamlit as st

def initialize_session_state():
    """Initializes persistent DataFrame tables inside Streamlit session state."""
    if 'event_log' not in st.session_state:
        st.session_state.event_log = pd.DataFrame(columns=[
            'Timestamp', 'System ID', 'Parameter Name', 'Recorded Value', 'Unit', 'Instantaneous Power (kW)', 'Operational Status'
        ])

    if 'telemetry_history' not in st.session_state:
        st.session_state.telemetry_history = pd.DataFrame(columns=[
            'Timestamp', 'Total_kW', 'AHU_kW', 'EF_kW', 'MDB_kW', 'Pump_kW', 'Power_Factor'
        ])

def record_telemetry_event(now_str: str, telemetry: dict):
    """Appends physical sensor readouts into the historical event log."""
    new_logs = [
        {"Timestamp": now_str, "System ID": "AHU-01", "Parameter Name": "Duct Differential Pressure", "Recorded Value": f"{telemetry['ahu']['pressure']:.1f}", "Unit": "Pa", "Instantaneous Power (kW)": f"{telemetry['ahu']['power_kw']:.2f}", "Operational Status": telemetry['ahu']['status']},
        {"Timestamp": now_str, "System ID": "AHU-01", "Parameter Name": "Supply Fan Speed", "Recorded Value": f"{telemetry['ahu']['fan_speed']:.1f}", "Unit": "%", "Instantaneous Power (kW)": f"{telemetry['ahu']['power_kw']:.2f}", "Operational Status": telemetry['ahu']['status']},
        {"Timestamp": now_str, "System ID": "EF-02", "Parameter Name": "Carbon Monoxide Sensor", "Recorded Value": f"{telemetry['ef']['co_ppm']:.1f}", "Unit": "PPM", "Instantaneous Power (kW)": f"{telemetry['ef']['power_kw']:.2f}", "Operational Status": telemetry['ef']['status']},
        {"Timestamp": now_str, "System ID": "MDB-01", "Parameter Name": "Power Factor", "Recorded Value": f"{telemetry['mdb']['pf']:.2f}", "Unit": "PF", "Instantaneous Power (kW)": f"{telemetry['mdb']['power_kw']:.2f}", "Operational Status": "ONLINE"},
        {"Timestamp": now_str, "System ID": "MDB-01", "Parameter Name": "Total Line Current", "Recorded Value": f"{telemetry['mdb']['current']:.1f}", "Unit": "A", "Instantaneous Power (kW)": f"{telemetry['mdb']['power_kw']:.2f}", "Operational Status": "ONLINE"},
        {"Timestamp": now_str, "System ID": "P-101", "Parameter Name": "Motor Current", "Recorded Value": f"{telemetry['pump']['current']:.1f}", "Unit": "A", "Instantaneous Power (kW)": f"{telemetry['pump']['power_kw']:.2f}", "Operational Status": telemetry['pump']['status']},
        {"Timestamp": now_str, "System ID": "P-101", "Parameter Name": "Discharge Flow Rate", "Recorded Value": f"{telemetry['pump']['flow_rate']:.1f}", "Unit": "L/min", "Instantaneous Power (kW)": f"{telemetry['pump']['power_kw']:.2f}", "Operational Status": telemetry['pump']['status']},
    ]

    st.session_state.event_log = pd.concat([pd.DataFrame(new_logs), st.session_state.event_log]).head(100)

    new_history = {
        'Timestamp': now_str,
        'Total_kW': telemetry['mdb']['power_kw'] + telemetry['pump']['power_kw'],
        'AHU_kW': telemetry['ahu']['power_kw'],
        'EF_kW': telemetry['ef']['power_kw'],
        'MDB_kW': telemetry['mdb']['power_kw'],
        'Pump_kW': telemetry['pump']['power_kw'],
        'Power_Factor': telemetry['mdb']['pf']
    }
    st.session_state.telemetry_history = pd.concat([st.session_state.telemetry_history, pd.DataFrame([new_history])]).tail(30)