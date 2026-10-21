import requests

def fetch_outdoor_temperature(api_key: str, city: str, fallback_temp: float) -> tuple[float, str]:
    """
    Fetches live outdoor ambient temperature from OpenWeatherMap API.
    Falls back gracefully to manual input if the API call fails or key is missing.
    """
    if not api_key:
        return fallback_temp, "Manual / Default Fallback"

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city},IN&appid={api_key}&units=metric"
    try:
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            data = response.json()
            return float(data['main']['temp']), f"Live API ({city})"
        return fallback_temp, "API Key Invalid / Fallback"
    except Exception:
        return fallback_temp, "Network Error / Fallback"