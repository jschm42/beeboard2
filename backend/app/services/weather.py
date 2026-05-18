import httpx
from typing import Optional, Dict, Any
from app.core.config import settings

async def fetch_current_weather(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """
    Fetches the current weather for a given latitude and longitude using OpenWeatherMap.
    """
    api_key = settings.OPENWEATHERMAP_API_KEY
    if not api_key:
        return None

    # URL based on https://openweathermap.org/api/one-call-3?collection=one_call_api#current
    # We use exclude=minutely,hourly,daily,alerts to only get current data
    url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=minutely,hourly,daily,alerts&units=metric&lang=de&appid={api_key}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0)
            if response.status_code == 200:
                data = response.json()
                return data.get("current")
            else:
                # Log error or handle gracefully
                print(f"Error fetching weather: {response.status_code} {response.text}")
                return None
        except Exception as e:
            print(f"Exception fetching weather: {e}")
            return None
