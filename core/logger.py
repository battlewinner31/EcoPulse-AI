import pandas as pd
import streamlit as st
from pathlib import Path

# Create a data folder if it doesn't exist
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

EVENT_LOG_FILE = DATA_DIR / "event_log.csv"
HISTORY_FILE = DATA_DIR / "telemetry_history.csv"


def initialize_session_state():
    """Load existing data from disk or create empty DataFrames."""
    
    if 'event_log' not in st.session_state:
        if EVENT_LOG_FILE.exists():
            st.session_state.event_log = pd.read_csv(EVENT_LOG_FILE)
        else:
            st.session_state.event_log = pd.DataFrame(columns=[
                'Timestamp', 'System ID', 'Parameter Name', 'Recorded Value',
                'Unit', 'Instantaneous Power (kW)', 'Operational Status'
            ])

    if 'telemetry_history' not in st.session_state:
        if HISTORY_FILE.exists():
            st.session_state.telemetry_history = pd.read_csv(HISTORY_FILE)
        else:
            st.session_state.telemetry_history = pd.DataFrame(columns=[
                'Timestamp', 'Total_kW', 'AHU_kW', 'EF_kW',
                'MDB_kW', 'Pump_kW', 'Power_Factor'
            ])


def record_telemetry_event(now_str: str, telemetry: dict):
    """Appends physical sensor readouts into the historical event log."""
    
    new_logs = [
        {
            "Timestamp": now_str,
            "System ID": "AHU-01",
            "Parameter Name": "Duct Differential Pressure",
            "Recorded Value": f"{telemetry['ahu']['pressure']:.1f}",
            "Unit": "Pa",
            "Instantaneous Power (kW)": f"{telemetry['ahu']['power_kw']:.2f}",
            "Operational Status": telemetry['ahu']['status']
        },
        {
            "Timestamp": now_str,
            "System ID": "AHU-01",
            "Parameter Name": "Supply Fan Speed",
            "Recorded Value": f"{telemetry['ahu']['fan_speed']:.1f}",
            "Unit": "%",
            "Instantaneous Power (kW)": f"{telemetry['ahu']['power_kw']:.2f}",
            "Operational Status": telemetry['ahu']['status']
        },
        {
            "Timestamp": now_str,
            "System ID": "EF-02",
            "Parameter Name": "Carbon Monoxide Sensor",
            "Recorded Value": f"{telemetry['ef']['co_ppm']:.1f}",
            "Unit": "PPM",
            "Instantaneous Power (kW)": f"{telemetry['ef']['power_kw']:.2f}",
            "Operational Status": telemetry['ef']['status']
        },
        {
            "Timestamp": now_str,
            "System ID": "MDB-01",
            "Parameter Name": "Power Factor",
            "Recorded Value": f"{telemetry['mdb']['pf']:.2f}",
            "Unit": "PF",
            "Instantaneous Power (kW)": f"{telemetry['mdb']['power_kw']:.2f}",
            "Operational Status": "ONLINE"
        },
        {
            "Timestamp": now_str,
            "System ID": "MDB-01",
            "Parameter Name": "Total Line Current",
            "Recorded Value": f"{telemetry['mdb']['current']:.1f}",
            "Unit": "A",
            "Instantaneous Power (kW)": f"{telemetry['mdb']['power_kw']:.2f}",
            "Operational Status": "ONLINE"
        },
        {
            "Timestamp": now_str,
            "System ID": "P-101",
            "Parameter Name": "Motor Current",
            "Recorded Value": f"{telemetry['pump']['current']:.1f}",
            "Unit": "A",
            "Instantaneous Power (kW)": f"{telemetry['pump']['power_kw']:.2f}",
            "Operational Status": telemetry['pump']['status']
        },
        {
            "Timestamp": now_str,
            "System ID": "P-101",
            "Parameter Name": "Discharge Flow Rate",
            "Recorded Value": f"{telemetry['pump']['flow_rate']:.1f}",
            "Unit": "L/min",
            "Instantaneous Power (kW)": f"{telemetry['pump']['power_kw']:.2f}",
            "Operational Status": telemetry['pump']['status']
        },
    ]

    st.session_state.event_log = pd.concat(
        [pd.DataFrame(new_logs), st.session_state.event_log]
    ).head(300)   # keep last 300 entries

    new_history = {
        'Timestamp': now_str,
        'Total_kW': telemetry['mdb']['power_kw'] + telemetry['pump']['power_kw'],
        'AHU_kW': telemetry['ahu']['power_kw'],
        'EF_kW': telemetry['ef']['power_kw'],
        'MDB_kW': telemetry['mdb']['power_kw'],
        'Pump_kW': telemetry['pump']['power_kw'],
        'Power_Factor': telemetry['mdb']['pf']
    }

    st.session_state.telemetry_history = pd.concat(
        [st.session_state.telemetry_history, pd.DataFrame([new_history])]
    ).tail(200)   # keep last 200 points for charts


def save_to_disk():
    """Save current session data to CSV files so it survives refresh."""
    try:
        st.session_state.event_log.to_csv(EVENT_LOG_FILE, index=False)
        st.session_state.telemetry_history.to_csv(HISTORY_FILE, index=False)
    except Exception as e:
        st.warning(f"Could not save data to disk: {e}")