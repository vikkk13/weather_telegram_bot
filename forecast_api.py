import requests
from datetime import datetime, timedelta

# Расшифровка кодов состояния погоды
WEATHER_CODES = {
    0: "☀ Ясно",
    1: "🌤 Почти ясно",
    2: "⛅ Переменная облачность",
    3: "☁ Пасмурно",

    45: "🌫 Туман",
    48: "🌫 Осаждающий иней",

    51: "🌦 Лёгкая морось",
    53: "🌦 Средняя морось",
    55: "🌧 Сильная морось",

    56: "🌦 Ледяная морось",
    57: "🌧 Лёдянная морось",

    61: "🌦 Лёгкий дождь",
    63: "🌧 Дождь",
    65: "🌧 Сильный дождь",

    66: "🌧 Ледяной дождь",
    67: "🌧 Сильный ледяной дождь",

    71: "🌨 Лёгкий снег",
    73: "🌨 Снег",
    75: "❄ Сильный снег",

    77: "❄ Снежная крупа",

    80: "🌧 Ливни (слабые)",
    81: "🌧 Ливни",
    82: "🌧 Ливни (сильные)",

    85: "🌨 Снежные ливни",
    86: "❄ Снежные ливни (сильные)",

    95: "⛈ Гроза",
    96: "⛈ Гроза с градом",
    99: "⛈ Сильная гроза с градом",
}


def get_coords(city: str):
    """Геокодинг города → lat / lon"""
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=ru"
    data = requests.get(url).json()

    if "results" not in data:
        return None, None

    result = data["results"][0]
    return result["latitude"], result["longitude"]


def get_hour_data(hourly_times, temps, codes, date, hour):
    """Получить температуру и код погоды для конкретного часа"""
    target = f"{date}T{hour:02d}:00"

    if target in hourly_times:
        idx = hourly_times.index(target)
        return temps[idx], codes[idx]
    return None, None


def get_forecast(city: str, tomorrow=False):
    """Получаем данные и формируем прогноз"""

    lat, lon = get_coords(city)
    if not lat:
        return None

    date = (
        (datetime.now() + timedelta(days=1)).date().isoformat()
        if tomorrow else datetime.now().date().isoformat()
    )

    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        f"&hourly=temperature_2m,weathercode"
        f"&timezone=auto"
    )
    data = requests.get(url).json()

    hourly_times = data["hourly"]["time"]
    temps = data["hourly"]["temperature_2m"]
    codes = data["hourly"]["weathercode"]

    # Часы, которые мы берём
    times_needed = {
        "🌅 Утро": 8,
        "🌞 День": 13,
        "🌇 Вечер": 19
    }

    result = []

    for part_name, hour in times_needed.items():
        temp, code = get_hour_data(hourly_times, temps, codes, date, hour)

        if temp is None:
            result.append((part_name, "нет данных", ""))
        else:
            weather_text = WEATHER_CODES.get(code, "Неизвестно")
            result.append((part_name, f"{temp:.1f}°C", weather_text))

    return result


def format_text(city: str, entries, tomorrow=False):
    day_word = "завтра" if tomorrow else "сегодня"
    text = f"📅 *Прогноз на {day_word} — {city}:*\n\n"

    for name, temp, weather in entries:
        if temp == "нет данных":
            text += f"*{name}:* нет данных\n\n"
        else:
            text += (
                f"*{name}:*\n"
                f"🌡 Температура: *{temp}*\n"
                f"{weather}\n\n"
            )

    return text


def get_today_text(city: str):
    data = get_forecast(city, tomorrow=False)
    if not data:
        return "❌ Город не найден."

    return format_text(city, data, tomorrow=False)


def get_tomorrow_text(city: str):
    data = get_forecast(city, tomorrow=True)
    if not data:
        return "❌ Город не найден."

    return format_text(city, data, tomorrow=True)
