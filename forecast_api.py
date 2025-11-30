import requests
from datetime import datetime, timedelta
from collections import Counter

# Таблица расшифровки кодов Open-Meteo
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
    """Получение координат города."""
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=ru"
    data = requests.get(url).json()
    if "results" not in data:
        return None, None

    r = data["results"][0]
    return r["latitude"], r["longitude"]


def load_hourly(city: str, tomorrow: bool = False):
    """Загрузка почасового прогноза на нужный день."""
    lat, lon = get_coords(city)
    if not lat:
        return None

    date = (datetime.now() + timedelta(days=1)).date().isoformat() if tomorrow else datetime.now().date().isoformat()

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

    # оставляем только строки нужного дня
    filtered = [
        (t, temp, code)
        for t, temp, code in zip(times, temps, codes)
        if t.startswith(date)
    ]

    return filtered


def filter_interval(hourly, start_h, end_h):
    """
    Берём диапазон часов (например 07–09),
    считаем среднюю температуру,
    выбираем наиболее частый weathercode.
    """

    segment = []
    for t, temp, code in hourly:
        hour = int(t[11:13])
        if start_h <= hour <= end_h:
            segment.append((temp, code))

    if not segment:
        return None, None

    # средняя температура
    avg_temp = sum(t for t, _ in segment) / len(segment)

    # наиболее частый weathercode
    codes = [c for _, c in segment]
    most_common = Counter(codes).most_common(1)[0][0]
    weather_text = WEATHER_CODES.get(most_common, "Неизвестно")

    return round(avg_temp, 1), weather_text


def build_text(city: str, forecast: dict, tomorrow=False):
    header = "завтра" if tomorrow else "сегодня"
    text = f"📅 *Прогноз на {header} — {city}:*\n\n"

    for part_name, data in forecast.items():
        temp, weather = data

        if temp is None:
            text += f"*{part_name}:* нет данных\n\n"
        else:
            text += (
                f"*{part_name}:*\n"
                f"🌡 Температура: *{temp}°C*\n"
                f"{weather}\n\n"
            )

    return text


def get_today_text(city: str):
    hourly = load_hourly(city, tomorrow=False)
    if not hourly:
        return "❌ Город не найден."

    forecast = {
        "🌅 Утро": filter_interval(hourly, 7, 9),
        "🌞 День": filter_interval(hourly, 12, 14),
        "🌇 Вечер": filter_interval(hourly, 18, 20),
    }

    return build_text(city, forecast, tomorrow=False)


def get_tomorrow_text(city: str):
    hourly = load_hourly(city, tomorrow=True)
    if not hourly:
        return "❌ Город не найден."

    forecast = {
        "🌅 Утро": filter_interval(hourly, 7, 9),
        "🌞 День": filter_interval(hourly, 12, 14),
        "🌇 Вечер": filter_interval(hourly, 18, 20),
    }

    return build_text(city, forecast, tomorrow=True)
