import asyncio
from datetime import datetime
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.client.default import DefaultBotProperties

from config import TOKEN
from database import (
    init_db, get_default_city, save_default_city,
    add_city, get_cities, set_sub_time,
    get_sub_time, delete_sub, get_all_subscriptions
)
from weather_api import get_weather
from inline_keyboards import main_menu, city_choice_menu, new_city_actions, subscription_menu
from reply_keyboards import bottom_menu
from forecast_api import get_today_text, get_tomorrow_text


async def scheduler(bot: Bot):
    """Ежедневная рассылка погоды"""
    while True:
        now = datetime.now().strftime("%H:%M")

        for user_id, t in get_all_subscriptions():
            if t == now:
                city = get_default_city(user_id)
                if city:
                    forecast = get_today_text(city)
                    try:
                        await bot.send_message(user_id, f"📨 Ежедневная рассылка:\n\n{forecast}")
                    except:
                        pass

        await asyncio.sleep(60)


async def main():
    init_db()

    bot = Bot(
        token=TOKEN,
        default=DefaultBotProperties(parse_mode="Markdown")
    )
    dp = Dispatcher()

    asyncio.create_task(scheduler(bot))

    # ============================================================
    # /start
    # ============================================================
    @dp.message(F.text == "/start")
    async def start_cmd(message: Message):
        user_id = message.from_user.id
        city = get_default_city(user_id)

        await message.answer("⏳ Загрузка меню...", reply_markup=bottom_menu())

        if not city:
            await message.answer("Введите ваш город (например: Москва):")
            return

        await message.answer(
            f"🌆 Ваш основной город: *{city}*",
            reply_markup=main_menu(city)
        )

    # ============================================================
    # Reply-кнопка "🏠 Меню"
    # ============================================================
    @dp.message(F.text == "🏠 Меню")
    async def bottom_menu_button(message: Message):
        user_id = message.from_user.id
        city = get_default_city(user_id)

        if not city:
            await message.answer("Введите ваш город:")
            return

        await message.answer(
            f"🌆 Ваш основной город: *{city}*",
            reply_markup=main_menu(city)
        )

    # ============================================================
    # Пользователь вводит текст — новый город
    # ============================================================
    @dp.message(F.text.regexp(r"^\d{2}-\d{2}$"))
    async def save_subscription_time(message: Message):
        """Обработка времени рассылки"""
        user_id = message.from_user.id
        raw = message.text

        hh, mm = raw.split("-")
        hh = int(hh)
        mm = int(mm)

        if not (0 <= hh <= 23 and 0 <= mm <= 59):
            await message.answer("❌ Неверный формат времени. Пример: 13-00")
            return

        time_str = f"{hh:02d}:{mm:02d}"
        set_sub_time(user_id, time_str)

        await message.answer(
            f"✅ Ежедневная рассылка установлена на *{time_str}*."
        )

    @dp.message(F.text)
    async def process_city_input(message: Message):
        """Обработка ввода города текстом"""
        user_id = message.from_user.id
        city = message.text.strip()

        weather = get_weather(city)
        if weather is None:
            await message.answer("❌ Город не найден, попробуйте снова.")
            return

        await message.answer(
            f"Город *{city}* найден.\nВыберите действие:",
            reply_markup=new_city_actions(city)
        )

    # ============================================================
    # CALLBACK-и (inline)
    # ============================================================

    @dp.callback_query(F.data == "show_weather")
    async def show_weather(callback: CallbackQuery):
        user_id = callback.from_user.id
        city = get_default_city(user_id)
        text = get_weather(city)

        await callback.message.answer(text)
        await callback.message.answer(
            f"🌆 Ваш основной город: *{city}*",
            reply_markup=main_menu(city)
        )

    @dp.callback_query(F.data == "today")
    async def today_forecast(callback: CallbackQuery):
        user_id = callback.from_user.id
        city = get_default_city(user_id)
        text = get_today_text(city)

        await callback.message.answer(text)
        await callback.message.answer(
            f"🌆 Ваш основной город: *{city}*",
            reply_markup=main_menu(city)
        )

    @dp.callback_query(F.data == "tomorrow")
    async def tomorrow_forecast(callback: CallbackQuery):
        user_id = callback.from_user.id
        city = get_default_city(user_id)
        text = get_tomorrow_text(city)

        await callback.message.answer(text)
        await callback.message.answer(
            f"🌆 Ваш основной город: *{city}*",
            reply_markup=main_menu(city)
        )

    @dp.callback_query(F.data == "choose_city")
    async def choose_city(callback: CallbackQuery):
        user_id = callback.from_user.id
        cities = get_cities(user_id)

        if not cities:
            await callback.message.answer("У вас нет сохранённых городов.")
            return

        await callback.message.answer(
            "Ваши города:",
            reply_markup=city_choice_menu(cities)
        )

    @dp.callback_query(F.data.startswith("city_"))
    async def selected_city(callback: CallbackQuery):
        city = callback.data.replace("city_", "")
        weather = get_weather(city)

        await callback.message.answer(weather)
        await callback.message.answer(
            "Выберите действие:",
            reply_markup=new_city_actions(city)
        )

    @dp.callback_query(F.data.startswith("make_default_"))
    async def make_default(callback: CallbackQuery):
        user_id = callback.from_user.id
        city = callback.data.replace("make_default_", "")
        save_default_city(user_id, city)

        await callback.message.answer(f"⭐ Город *{city}* установлен как основной.")
        await callback.message.answer(
            f"🌆 Ваш основной город: *{city}*",
            reply_markup=main_menu(city)
        )

    @dp.callback_query(F.data.startswith("save_city_"))
    async def save_city(callback: CallbackQuery):
        user_id = callback.from_user.id
        city = callback.data.replace("save_city_", "")
        add_city(user_id, city)

        await callback.message.answer(f"📌 Город *{city}* добавлен в список.")
        await callback.message.answer(
            f"🌆 Ваш основной город: *{get_default_city(user_id)}*",
            reply_markup=main_menu(get_default_city(user_id))
        )

    @dp.callback_query(F.data.startswith("just_show_"))
    async def just_show(callback: CallbackQuery):
        city = callback.data.replace("just_show_", "")
        text = get_weather(city)

        await callback.message.answer(text)
        await callback.message.answer(
            "Выберите действие:",
            reply_markup=new_city_actions(city)
        )

    @dp.callback_query(F.data == "subscription")
    async def subscription_menu_open(callback: CallbackQuery):
        user_id = callback.from_user.id
        time = get_sub_time(user_id)

        text = (
            "🕒 *Ежедневная рассылка погоды*\n\n"
            "Вы можете каждый день автоматически получать прогноз погоды.\n\n"
            f"Текущее время рассылки: *{time if time else 'не задано'}*\n"
        )

        await callback.message.answer(
            text,
            reply_markup=subscription_menu()
        )

    @dp.callback_query(F.data == "sub_set")
    async def subscription_set(callback: CallbackQuery):
        await callback.message.answer(
            "⌚ Введите время для рассылки в формате `14-30`:",
            reply_markup=None
        )

    @dp.callback_query(F.data == "sub_cancel")
    async def subscription_cancel(callback: CallbackQuery):
        user_id = callback.from_user.id
        delete_sub(user_id)

        await callback.message.answer("❌ Рассылка отменена.")
        await callback.message.answer(
            f"🌆 Ваш основной город: *{get_default_city(user_id)}*",
            reply_markup=main_menu(get_default_city(user_id))
        )

    @dp.callback_query(F.data == "help")
    async def help_callback(callback: CallbackQuery):
        user_id = callback.from_user.id
        city = get_default_city(user_id)

        help_text = (
            "ℹ️ *Помощь по боту погоды*\n\n"
            "Вот что умеет этот бот:\n\n"
            "• *🌤 Погода в {city}* — показывает текущую погоду в вашем основном городе: температура, ветер и краткое описание.\n"
            "• *📅 Прогноз на сегодня* — даёт прогноз на сегодня, разбитый на утро, день и вечер.\n"
            "• *📅 Прогноз на завтра* — то же самое, но для завтрашнего дня.\n"
            "• *🌆 Выбрать другой город* — показывает список ранее сохранённых городов, можно быстро посмотреть погоду в любом из них.\n"
            "• *➕ Добавить новый город* — вы вводите название города, бот проверяет, и предлагает:\n"
            "   — сделать его основным;\n"
            "   — добавить в список городов;\n"
            "   — просто один раз показать погоду.\n"
            "• *🕒 Настроить рассылку* — бот каждый день в заданное время будет присылать прогноз на сегодня для вашего основного города.\n"
            "   — *Установить / изменить время* — введите время в формате `ЧЧ-ММ`, например `08-30`;\n"
            "   — *Отменить рассылку* — отключает ежедневные сообщения.\n\n"
            "• Кнопка *🏠 Меню* внизу экрана — всегда открывает главное меню с кнопками.\n\n"
            "Если что-то работает не так, как ожидаете — просто напишите новый город или нажмите 🏠 Меню."
        ).format(city=city if city else "вашем городе")

        # отправляем помощь отдельным сообщением
        await callback.message.answer(help_text)

        # и сразу следом — меню
        if city:
            await callback.message.answer(
                f"🌆 Ваш основной город: *{city}*",
                reply_markup=main_menu(city)
            )
        else:
            await callback.message.answer(
                "У вас ещё не задан основной город. Введите его текстом (например: Москва)."
            )


    # запуск бота
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
