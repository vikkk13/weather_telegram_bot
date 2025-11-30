import requests
from datetime import datetime, timedelta

# Расшифровка кодов состояния погоды (WMO)
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

    56: "🌦 Лёгкая ледяная морось",
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


def get_tomorrow_forecast(city: str):
    """Почасовой прогноз на завтра"""
    # Геокодинг
    geo = requests.get(
        f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
    ).json()
    if "results" not in geo:
        return None

    lat = geo["results"][0]["latitude"]
    lon = geo["results"][0]["longitude"]

    # Определяем дату завтра
    tomorrow = (datetime.utcnow() + timedelta(days=1)).date().isoformat()

    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        f"&hourly=temperature_2m,weathercode"
        f"&timezone=auto"
    )

    data = requests.get(url).json()

    times = data["hourly"]["time"]
    temps = data["hourly"]["temperature_2m"]
    codes = data["hourly"]["weathercode"]

    result = []
    for t, temp, code in zip(times, temps, codes):
        if t.startswith(tomorrow):
            result.append((t, temp, code))

    return result


def split_day_parts(hourly):
    morning, day, evening = [], [], []

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
    if not data:
        return f"*{title}:* нет данных\n\n"

    temps = [temp for _, temp, _ in data]
    codes = [code for _, _, code in data]

    avg_temp = round(sum(temps) / len(temps), 1)
    main_code = max(set(codes), key=codes.count)

    return (
        f"*{title}:*\n"
        f"🌡 Температура: *{avg_temp}°C*\n"
        f"{WEATHER_CODES.get(main_code, 'Неизвестно')}\n\n"
    )


def get_tomorrow_text(city: str):
    hourly = get_tomorrow_forecast(city)
    if hourly is None:
        return "❌ Город не найден."

    morning, day, evening = split_day_parts(hourly)

    text = f"📅 *Прогноз на завтра — {city}:*\n\n"
    text += format_block("🌅 Утро", morning)
    text += format_block("🌞 День", day)
    text += format_block("🌇 Вечер", evening)

    return text


def get_today_forecast(city: str):
    """Почасовой прогноз на сегодня"""

    # Геокодинг
    geo = requests.get(
        f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
    ).json()
    if "results" not in geo:
        return None

    lat = geo["results"][0]["latitude"]
    lon = geo["results"][0]["longitude"]

    # ВАЖНО! Локальная дата, а не UTC
    today = datetime.now().date().isoformat()

    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        f"&hourly=temperature_2m,weathercode"
        f"&timezone=auto"
    )

    data = requests.get(url).json()

    times = data["hourly"]["time"]
    temps = data["hourly"]["temperature_2m"]
    codes = data["hourly"]["weathercode"]

    result = []
    for t, temp, code in zip(times, temps, codes):
        if t.startswith(today):   # теперь совпадает
            result.append((t, temp, code))

    return result


def get_today_text(city: str):
    hourly = get_today_forecast(city)
    if hourly is None:
        return "❌ Город не найден."

    morning, day, evening = split_day_parts(hourly)

    text = f"📅 *Прогноз на сегодня — {city}:*\n\n"
    text += format_block("🌅 Утро", morning)
    text += format_block("🌞 День", day)
    text += format_block("🌇 Вечер", evening)

    return text
