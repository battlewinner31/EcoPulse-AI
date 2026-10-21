import streamlit as st
import config
from core.weather import fetch_outdoor_temperature

def render_sidebar() -> dict:
    """Renders all interactive sidebar controls and returns state dictionary."""
    st.sidebar.title("🏭 Facility Control Interface")
    st.sidebar.markdown("---")

    st.sidebar.subheader("🌐 Environmental Data Source")
    weather_source = st.sidebar.radio(
        "Outdoor Weather Provider",
        ["Manual Simulator Sliders", "Live OpenWeatherMap API"],
        index=0
    )

    fallback_temp = config.DEFAULT_OUTDOOR_TEMP_C
    outdoor_temp = fallback_temp
    weather_info = "Manual Input"

    if weather_source == "Live OpenWeatherMap API":
        api_key = st.sidebar.text_input("OpenWeatherMap API Key", type="password")
        city_name = st.sidebar.selectbox("City Selection", ["Bengaluru", "Delhi", "Mumbai", "Chennai", "Kolkata"])
        
        if api_key:
            outdoor_temp, weather_info = fetch_outdoor_temperature(api_key, city_name, fallback_temp)
        else:
            st.sidebar.info("Enter API Key above to fetch live weather.")
            outdoor_temp = st.sidebar.slider("Outdoor Ambient Temp (°C)", 20.0, 45.0, 32.0, 0.5)
    else:
        outdoor_temp = st.sidebar.slider("Outdoor Ambient Temp (°C)", 20.0, 45.0, 32.0, 0.5)

    building_occupancy = st.sidebar.slider("Building Occupancy (People)", 0, 100, config.DEFAULT_OCCUPANCY)

    st.sidebar.markdown("---")
    st.sidebar.subheader("⚡ Physical Equipment State Toggles")

    sim_ahu_resistance = st.sidebar.checkbox("Simulate AHU Air Duct Resistance Increase", value=False)
    sim_co_shift = st.sidebar.checkbox("Simulate Basement Gas Concentration Shift (>30 PPM CO)", value=False)
    sim_pf_drop = st.sidebar.checkbox("Simulate Electrical Load Power Factor Drop", value=False)
    sim_pump_cavitation = st.sidebar.checkbox("Simulate Pump Suction Line Cavitation", value=False)

    return {
        "outdoor_temp": outdoor_temp,
        "building_occupancy": building_occupancy,
        "sim_ahu_resistance": sim_ahu_resistance,
        "sim_co_shift": sim_co_shift,
        "sim_pf_drop": sim_pf_drop,
        "sim_pump_cavitation": sim_pump_cavitation,
        "weather_info": weather_info
    }