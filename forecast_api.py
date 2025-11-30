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
    57: "🌧 Сильная ледяная морось",

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
    """Геокодинг города → lat/lon"""
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=ru"
    data = requests.get(url).json()

    if "results" not in data:
        return None, None

    result = data["results"][0]
    return result["latitude"], result["longitude"]


def get_hourly(city: str, for_tomorrow=False):
    """Получение почасового прогноза"""

    lat, lon = get_coords(city)
    if not lat:
        return None

    date = (
        (datetime.now() + timedelta(days=1)).date().isoformat()
        if for_tomorrow
        else datetime.now().date().isoformat()
    )

    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        f"&hourly=temperature_2m,weathercode"
        f"&timezone=auto"
    )

    data = requests.get(url).json()
    times  = data["hourly"]["time"]
    temps  = data["hourly"]["temperature_2m"]
    codes  = data["hourly"]["weathercode"]

    filtered = []
    for t, temp, code in zip(times, temps, codes):
        if t.startswith(date):
            filtered.append((t, temp, code))

    return filtered


def split_by_parts(hourly):
    """Деление на утро / день / вечер"""

    morning = []
    day = []
    evening = []

    for t, temp, code in hourly:
        hour = int(t[11:13])

        if 6 <= hour <= 11:
            morning.append((t, temp, code))
        elif 12 <= hour <= 17:
            day.append((t, temp, code))
        elif 18 <= hour <= 23:
            evening.append((t, temp, code))

    return morning, day, evening


def format_block(title, data):
    """Форматирование блока (утро/день/вечер)"""

    if not data:
        return f"*{title}:* нет данных\n\n"

    # температура — МАКСИМУМ (как делают все погодные сервисы)
    max_temp = max(temp for _, temp, _ in data)

    # состояние погоды — самое частое
    codes = [code for _, _, code in data]
    main_code = max(set(codes), key=codes.count)
    weather_text = WEATHER_CODES.get(main_code, "Неизвестно")

    return (
        f"*{title}:*\n"
        f"🌡 Температура: *{max_temp:.1f}°C*\n"
        f"{weather_text}\n\n"
    )


def get_today_text(city: str):
    hourly = get_hourly(city, for_tomorrow=False)
    if not hourly:
        return "❌ Город не найден."

    morning, day, evening = split_by_parts(hourly)

    text = f"📅 *Прогноз на сегодня — {city}:*\n\n"
    text += format_block("🌅 Утро", morning)
    text += format_block("🌞 День", day)
    text += format_block("🌇 Вечер", evening)

    return text


def get_tomorrow_text(city: str):
    hourly = get_hourly(city, for_tomorrow=True)
    if not hourly:
        return "❌ Город не найден."

    morning, day, evening = split_by_parts(hourly)

    text = f"📅 *Прогноз на завтра — {city}:*\n\n"
    text += format_block("🌅 Утро", morning)
    text += format_block("🌞 День", day)
    text += format_block("🌇 Вечер", evening)

    return text
