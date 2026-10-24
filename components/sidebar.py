# components/sidebar.py
import streamlit as st
import config
from core.weather import fetch_outdoor_temperature


def render_sidebar() -> dict:
    """Renders all interactive sidebar controls and returns state dictionary."""

    st.sidebar.title("Facility Control Interface")
    st.sidebar.markdown("---")

    # -------------------------------------------------
    # 1. Initialize session state ONLY if the key does not exist
    # -------------------------------------------------
    defaults = {
        "sim_ahu_resistance": False,
        "sim_co_shift": False,
        "sim_pf_drop": False,
        "sim_pump_cavitation": False,
        "outdoor_temp_slider": 32.0,
        "occupancy": config.DEFAULT_OCCUPANCY,
    }

    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

    # -------------------------------------------------
    # 2. Environmental Data
    # -------------------------------------------------
    st.sidebar.subheader("Environmental Data Source")

    weather_source = st.sidebar.radio(
        "Outdoor Weather Provider",
        ["Manual Simulator Sliders", "Live OpenWeatherMap API"],
        key="weather_source"
    )

    outdoor_temp = st.session_state.get("outdoor_temp_slider", 32.0)

    if weather_source == "Live OpenWeatherMap API":
        api_key = st.sidebar.text_input("OpenWeatherMap API Key", type="password", key="owm_api_key")
        city_name = st.sidebar.selectbox(
            "City Selection",
            ["Bengaluru", "Delhi", "Mumbai", "Chennai", "Kolkata"],
            key="city_name"
        )

        if api_key:
            outdoor_temp, _ = fetch_outdoor_temperature(api_key, city_name, config.DEFAULT_OUTDOOR_TEMP_C)
        else:
            st.sidebar.info("Enter API Key above to fetch live weather.")
            outdoor_temp = st.sidebar.slider(
                "Outdoor Ambient Temp (°C)",
                20.0, 45.0,
                key="outdoor_temp_slider"
            )
    else:
        outdoor_temp = st.sidebar.slider(
            "Outdoor Ambient Temp (°C)",
            20.0, 45.0,
            key="outdoor_temp_slider"
        )

    building_occupancy = st.sidebar.slider(
        "Building Occupancy (People)",
        0, 100,
        key="occupancy"
    )

    st.sidebar.markdown("---")
    st.sidebar.subheader("Physical Equipment State Toggles")

    # -------------------------------------------------
    # 3. Fault Toggles – ONLY use key= (no value=)
    # This is the critical fix
    # -------------------------------------------------
    sim_ahu_resistance = st.sidebar.checkbox(
        "Simulate AHU Air Duct Resistance Increase",
        key="sim_ahu_resistance"
    )

    sim_co_shift = st.sidebar.checkbox(
        "Simulate Basement Gas Concentration Shift (>30 PPM CO)",
        key="sim_co_shift"
    )

    sim_pf_drop = st.sidebar.checkbox(
        "Simulate Electrical Load Power Factor Drop",
        key="sim_pf_drop"
    )

    sim_pump_cavitation = st.sidebar.checkbox(
        "Simulate Pump Suction Line Cavitation",
        key="sim_pump_cavitation"
    )

    # -------------------------------------------------
    # 4. Return current values
    # -------------------------------------------------
    return {
        "outdoor_temp": outdoor_temp,
        "building_occupancy": building_occupancy,
        "sim_ahu_resistance": sim_ahu_resistance,
        "sim_co_shift": sim_co_shift,
        "sim_pf_drop": sim_pf_drop,
        "sim_pump_cavitation": sim_pump_cavitation,
    }