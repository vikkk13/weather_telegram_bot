import requests
from forecast_api import WEATHER_CODES   # ДОБАВИЛИ ЭТО

# Функция получает прогноз:
# 1) делает геокодинг (город → координаты)
# 2) запрашивает погоду из Open-Meteo


def get_weather(city: str) -> str | None:
    # 1. Геокодинг
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
    geo = requests.get(geo_url).json()

    if "results" not in geo:
        return None

    lat = geo["results"][0]["latitude"]
    lon = geo["results"][0]["longitude"]

    # 2. Текущая погода
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        f"&current_weather=true"
    )
    data = requests.get(url).json()

    temp = data["current_weather"]["temperature"]
    wind = data["current_weather"]["windspeed"]
    code = int(data["current_weather"]["weathercode"])  # ВАЖНО: в int
    desc = WEATHER_CODES.get(code, "Неизвестное состояние")

    return (
        f"🌆 *Погода в городе {city}:*\n"
        f"🌡 Температура: *{temp}°C*\n"
        f"💨 Ветер: *{wind} км/ч*\n"
        f"{desc}"
    )