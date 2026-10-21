import numpy as np

def simulate_ahu(sim_resistance: bool, outdoor_temp: float) -> dict:
    """Calculates AHU-01 physical telemetry based on duct resistance state."""
    if sim_resistance:
        pressure = 310.0 + np.random.uniform(-3, 3)
        fan_speed = 92.0 + np.random.uniform(-0.5, 0.5)
        power_kw = 22.8 + np.random.uniform(-0.2, 0.2)
        status = "HIGH RESISTANCE RUN"
    else:
        pressure = 120.0 + np.random.uniform(-2, 2)
        fan_speed = 60.0 + np.random.uniform(-0.5, 0.5)
        power_kw = 11.2 + np.random.uniform(-0.1, 0.1)
        status = "NOMINAL RUN"

    return {
        "pressure": pressure,
        "fan_speed": fan_speed,
        "cfm": 1000.0 + np.random.uniform(-10, 10),
        "power_kw": power_kw,
        "supply_temp": max(14.0, outdoor_temp - 12.0),
        "status": status
    }

def simulate_ef(sim_co_shift: bool) -> dict:
    """Calculates EF-02 basement gas concentration and ventilation state."""
    if sim_co_shift:
        co_ppm = 38.0 + np.random.uniform(-1.0, 1.0)
        power_kw = 11.5 + np.random.uniform(-0.1, 0.1)
        status = "HIGH PURGE"
    else:
        co_ppm = 12.0 + np.random.uniform(-0.5, 0.5)
        power_kw = 2.8 + np.random.uniform(-0.05, 0.05)
        status = "LOW"

    return {
        "co_ppm": co_ppm,
        "power_kw": power_kw,
        "status": status
    }

def simulate_mdb(sim_pf_drop: bool, ahu_kw: float, ef_kw: float) -> dict:
    """Calculates Main Electrical Distribution Panel 3-phase telemetry."""
    voltage = 415.0 + np.random.uniform(-2.0, 2.0)
    
    if sim_pf_drop:
        pf = 0.78 + np.random.uniform(-0.01, 0.01)
        power_kw = (ahu_kw + ef_kw + 25.0) * 1.18
    else:
        pf = 0.95 + np.random.uniform(-0.005, 0.005)
        power_kw = ahu_kw + ef_kw + 25.0

    current = (power_kw * 1000) / (np.sqrt(3) * voltage * pf)
    
    return {
        "voltage": voltage,
        "current": current,
        "pf": pf,
        "power_kw": power_kw
    }

def simulate_pump(sim_cavitation: bool) -> dict:
    """Calculates Plumbing Pump P-101 motor electrical and hydro telemetry."""
    if sim_cavitation:
        tank_level = 18.0 + np.random.uniform(-0.2, 0.2)
        current = 6.1 + np.random.uniform(-0.1, 0.1)
        flow_rate = 15.0 + np.random.uniform(-1.0, 1.0)
        power_kw = 1.8 + np.random.uniform(-0.05, 0.05)
    else:
        tank_level = 45.0 + np.random.uniform(-0.1, 0.1)
        current = 14.2 + np.random.uniform(-0.2, 0.2)
        flow_rate = 120.0 + np.random.uniform(-2.0, 2.0)
        power_kw = 4.5 + np.random.uniform(-0.1, 0.1)

    return {
        "tank_level": tank_level,
        "current": current,
        "flow_rate": flow_rate,
        "power_kw": power_kw,
        "status": "RUN"
    }