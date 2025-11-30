from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu(default_city: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🌤 Погода в {default_city}", callback_data="show_weather")],
        [InlineKeyboardButton(text="📅 Прогноз на сегодня", callback_data="today")],
        [InlineKeyboardButton(text="📅 Прогноз на завтра", callback_data="tomorrow")],
        [InlineKeyboardButton(text="🌆 Выбрать другой город", callback_data="choose_city")],
        [InlineKeyboardButton(text="➕ Добавить новый город", callback_data="add_city")],
        [InlineKeyboardButton(text="🕒 Настроить рассылку", callback_data="subscription")],
        [InlineKeyboardButton(text="ℹ️ Помощь", callback_data="help")]
    ])


def subscription_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏱ Установить / изменить время", callback_data="sub_set")],
        [InlineKeyboardButton(text="❌ Отменить рассылку", callback_data="sub_cancel")],
        [InlineKeyboardButton(text="⬅ Назад", callback_data="back_main")]
    ])



def city_choice_menu(cities: list[str]):
    keyboard = []

    for city in cities:
        keyboard.append([InlineKeyboardButton(
            text=f"🏙 {city}",
            callback_data=f"city_{city}"
        )])

    keyboard.append([InlineKeyboardButton(
        text="⬅ Назад",
        callback_data="back_main"
    )])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def new_city_actions(city: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="⭐ Сделать городом по умолчанию",
            callback_data=f"make_default_{city}"
        )],
        [InlineKeyboardButton(
            text="📌 Добавить в список",
            callback_data=f"save_city_{city}"
        )],
        [InlineKeyboardButton(
            text="👀 Просто показать погоду",
            callback_data=f"just_show_{city}"
        )],
        [InlineKeyboardButton(
            text="⬅ Назад",
            callback_data="back_main"
        )]
    ])
