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

    # We use the free 2.5 weather API, which doesn't require a paid subscription/One Call plan
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&lang=de&appid={api_key}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0)
            if response.status_code == 200:
                data = response.json()
                # Map to structure expected by chatbot/agent loop (temp, humidity, wind_speed, weather)
                return {
                    "temp": data.get("main", {}).get("temp", 0.0),
                    "humidity": data.get("main", {}).get("humidity", 0),
                    "wind_speed": data.get("wind", {}).get("speed", 0.0),
                    "weather": data.get("weather", [])
                }
            else:
                # Log error or handle gracefully
                print(f"Error fetching weather: {response.status_code} {response.text}")
                return None
        except Exception as e:
            print(f"Exception fetching weather: {e}")
            return None

def fetch_current_weather_sync(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """Synchronous version of fetch_current_weather."""
    import asyncio
    try:
        loop = asyncio.get_running_loop()
        return loop.run_until_complete(fetch_current_weather(lat, lon))
    except RuntimeError:
        return asyncio.run(fetch_current_weather(lat, lon))

async def geocode_address(address: str) -> Optional[Dict[str, Any]]:
    """
    Geocodes an address query using OpenWeatherMap Geocoding API.
    Falls back to OpenStreetMap Nominatim if OpenWeatherMap key is invalid/unconfigured or fails.
    """
    api_key = settings.OPENWEATHERMAP_API_KEY
    if api_key:
        url = f"https://api.openweathermap.org/geo/1.0/direct?q={address}&limit=1&appid={api_key}"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, timeout=10.0)
                if response.status_code == 200:
                    data = response.json()
                    if data and isinstance(data, list) and len(data) > 0:
                        first = data[0]
                        return {
                            "lat": first.get("lat"),
                            "lon": first.get("lon"),
                            "name": first.get("name"),
                            "country": first.get("country"),
                            "state": first.get("state")
                        }
                else:
                    print(f"OpenWeatherMap geocoding failed (status {response.status_code}): {response.text}")
            except Exception as e:
                print(f"Exception during OpenWeatherMap geocoding: {e}")

    # Fallback to OpenStreetMap Nominatim
    print("Falling back to OpenStreetMap Nominatim for geocoding...")
    url = f"https://nominatim.openstreetmap.org/search?q={address}&format=json&limit=1"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers={"User-Agent": "BeeBoard/1.0"}, timeout=10.0)
            if response.status_code == 200:
                data = response.json()
                if data and isinstance(data, list) and len(data) > 0:
                    first = data[0]
                    return {
                        "lat": float(first.get("lat")),
                        "lon": float(first.get("lon")),
                        "name": first.get("display_name").split(",")[0],
                        "country": first.get("display_name").split(",")[-1].strip(),
                        "state": None
                    }
            else:
                print(f"Nominatim geocoding failed (status {response.status_code}): {response.text}")
        except Exception as e:
            print(f"Exception during Nominatim geocoding fallback: {e}")

    return None

