from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.types import BufferedInputFile
import asyncio
import buttons
import plots
import tokens
from db import DataBase
from pomodoro import Pomodoro
from timer import Timer

db = DataBase('pomodoro.db')
bot = Bot(tokens.TG_BOT)
dp = Dispatcher()
last_chat_id = None

pomodoro_sessions = {}
timers = {}


async def send_info_stats(user_id: int, chat_id: int):
    sessions = db.get_numbers_of_sessions(user_id)
    minutes = db.get_numbers_of_minutes(user_id)
    if sessions is None:
        await bot.send_message(chat_id, 'У вас еще нет завершенных сессий 🍅')
    else:
        await bot.send_message(chat_id, f'Завершенных сессий Pomodoro: {sessions} 🍅\nВсего минут работы: {minutes} ⌛')


async def send_weekly_stats(user_id: int, chat_id: int):
    result = db.get_stats_per_week(user_id)
    if result:
        buf = plots.send_weekly_plot(result)
        photo_input_file = BufferedInputFile(buf.read(), filename="tmp.png")
        await bot.send_photo(chat_id, photo=photo_input_file)
        buf.close()
    else:
        await bot.send_message(chat_id, 'Пока ни одной закрытой помидорки за неделю 🍅')


async def send_hourly_stats(user_id: int, chat_id: int):
    result = db.get_stats_per_hour(user_id)
    if result:
        buf = plots.send_hourly_plot(result)
        photo_input_file = BufferedInputFile(buf.read(), filename="tmp.png")
        await bot.send_photo(chat_id, photo=photo_input_file)
        buf.close()
    else:
        await bot.send_message(chat_id, 'Пока ни одной закрытой помидорки за сегодня 🍅')


async def end_timer(user_id: int, chat_id: int, minutes: int):
    await bot.send_message(chat_id, f"Ваш таймер на {minutes} минут закончился❗")
    db.update_stats(user_id, minutes)
    db.update_timer_state(user_id, 0)
    del timers[user_id]


async def end_sprint(user_id: int, chat_id: int, minutes: int, cycles: int):
    await bot.send_message(chat_id, f"Спринт завершен! 🎉 +{minutes * cycles} продуктивных минут")
    db.update_stats(user_id, minutes)
    db.update_timer_state(user_id, 0)
    del pomodoro_sessions[user_id]


async def end_pomodoro(user_id: int, chat_id: int, minutes: int):
    await bot.send_message(chat_id, "Помодоро завершен ✅ Немного отдохните")
    db.update_stats(user_id, minutes)


async def end_break(chat_id: int):
    await bot.send_message(chat_id, "Перерыв закончился❗")


@dp.message(Command("start"))
async def start(message: types.Message):
    global last_chat_id
    last_chat_id = message.chat.id
    if not db.user_exists(message.from_user.id):
        db.add_user(message.from_user.id)
    await bot.send_message(message.chat.id, buttons.START_PROMPT)
    await bot.send_message(message.chat.id, 'Выберите команду 🔽', reply_markup=buttons.start())


@dp.message(Command("menu"))
async def menu(message: types.Message):
    global last_chat_id
    last_chat_id = message.chat.id
    await bot.send_message(message.chat.id, 'Выберите команду 🔽', reply_markup=buttons.start())


async def stats(message: types.Message):
    global last_chat_id
    last_chat_id = message.chat.id
    await bot.send_message(message.chat.id, "Выберите тип статистики 🔽", reply_markup=buttons.stats())


@dp.message(Command("test_error"))
async def test_error(message: types.Message):
    global last_chat_id
    last_chat_id = message.chat.id
    raise ValueError("тестовое исключение")


@dp.message()
async def handle_text(message: types.Message):
    global last_chat_id
    last_chat_id = message.chat.id
    if message.text == 'Поставить таймер ⏲️':
        await pomodoro(message)
    elif message.text == 'Отобразить статистику 📊':
        await stats(message)
    elif message.text == 'Запустить спринт 🚀':
        await sprint(message)
    elif message.text == 'Настроить спринт ⚙️':
        await settings(message)
    else:
        await bot.send_message(message.from_user.id, 'Такого я, к сожалению, не умею ❌')


async def settings(message: types.Message):
    global msg_with_settings
    global last_chat_id
    last_chat_id = message.chat.id
    minutes, short_break, long_break, cycles = db.get_user_settings(message.from_user.id)
    msg_with_settings = await bot.send_message(message.chat.id,
                                               f"Ваши настройки 🛠\n\n"
                                               f"Работа 💼 = {minutes} минут\n"
                                               f"Короткий перерыв ⏳ = {short_break} минут\n"
                                               f"Длинный перерыв ☕️ = {long_break} минут\n"
                                               f"Кол-во циклов 🍅 = {cycles}",
                                               reply_markup=buttons.settings())


async def updated_settings(msg_with_settings, user_id):
    minutes, short_break, long_break, cycles = db.get_user_settings(user_id)
    await bot.edit_message_text(chat_id=msg_with_settings.chat.id, message_id=msg_with_settings.message_id,
                                text=f"Ваши настройки 🛠\n\n"
                                     f"Работа 💼 = {minutes} минут\n"
                                     f"Короткий перерыв ⏳ = {short_break} минут\n"
                                     f"Длинный перерыв ☕️ = {long_break} минут\n"
                                     f"Кол-во циклов 🍅 = {cycles}",
                                reply_markup=buttons.settings())


async def pomodoro(message: types.Message):
    global last_chat_id
    last_chat_id = message.chat.id
    user_id = message.from_user.id

    if db.get_timer_state(user_id):
        await bot.send_message(message.chat.id, "У вас уже запущен таймер. Дождитесь его завершения ⏰")
        return

    await bot.send_message(message.from_user.id, "На сколько установить таймер? ⏰", reply_markup=buttons.pomodoro())


async def sprint(message: types.Message):
    global message_to_edit
    global last_chat_id
    last_chat_id = message.chat.id
    if db.get_timer_state(message.from_user.id):
        await bot.send_message(message.chat.id, "Вы уже начали спринт/таймер ⏰\nДождитесь его завершения.")
        return
    else:
        db.update_timer_state(message.chat.id, 1)
    minutes, short_break, long_break, cycles = db.get_user_settings(message.from_user.id)
    message_to_edit = await bot.send_message(message.from_user.id,
                                             f"Спринт на {cycles} цикла каждый по {minutes} минут запущен! 🚀"
                                             , reply_markup=buttons.active_sprint())
    pomodoro_sessions[message.from_user.id] = Pomodoro(message.from_user.id, minutes, short_break, long_break, cycles,
                                                       lambda: end_pomodoro(message.from_user.id, message.chat.id,
                                                                            minutes),
                                                       lambda: end_break(message.chat.id),
                                                       lambda: end_sprint(message.from_user.id, message.chat.id,
                                                                          minutes, cycles))
    await pomodoro_sessions[message.from_user.id].start_pomodoro_session()


@dp.callback_query()
async def query_handler(call: types.CallbackQuery):
    global last_chat_id
    last_chat_id = call.message.chat.id
    global message_to_edit
    global msg_with_settings
    user_id = call.from_user.id
    if call.data.isdigit():  # Если callback_data - это число, запускаем таймер
        if db.get_timer_state(call.message.chat.id):
            await bot.send_message(call.message.chat.id, "Вы уже начали спринт/таймер ⏰\nДождитесь его завершения.")
            return
        else:
            db.update_timer_state(user_id, 1)
        duration = int(call.data)
        await bot.answer_callback_query(callback_query_id=call.id, text='Таймер запущен!')
        message_to_edit = await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                      text=f'Таймер запущен на {duration} минут ⏰',
                                                      reply_markup=buttons.active_timer())
        timers[user_id] = Timer(user_id, duration,
                                lambda: end_timer(user_id, call.message.chat.id, duration))
        await timers[user_id].start()

    elif call.data == 'info_stats':
        await send_info_stats(user_id, call.message.chat.id)
    elif call.data == 'weekly_stats':
        await send_weekly_stats(user_id, call.message.chat.id)
    elif call.data == 'hourly_stats':
        await send_hourly_stats(user_id, call.message.chat.id)
    elif call.data == 'time_left':
        if user_id in timers and timers[user_id].is_running():
            remaining_time = timers[user_id].get_remaining_time()
            await bot.answer_callback_query(callback_query_id=call.id, text=f'Осталось {remaining_time} мин. ⏳')
        else:
            await bot.answer_callback_query(callback_query_id=call.id, text="У вас не запущен таймер.")

    elif call.data == 'stop_timer':
        if user_id in timers:
            db.update_timer_state(user_id, 0)
            timers[user_id].cancel()
            del timers[user_id]
            await bot.send_message(call.message.chat.id, f'Таймер отменен⛔')
        else:
            await bot.answer_callback_query(callback_query_id=call.id, text="У вас не запущен таймер.")
    elif call.data == 'sprint_left':
        if user_id in pomodoro_sessions:
            remaining_time = pomodoro_sessions[user_id].time_remaining()
            await bot.answer_callback_query(callback_query_id=call.id, text=f'Осталось {remaining_time} мин. ⏳')
        else:
            await bot.answer_callback_query(callback_query_id=call.id, text="У вас не запущен спринт")

    elif call.data == 'stop_sprint':
        if user_id in pomodoro_sessions:
            db.update_timer_state(user_id, 0)
            pomodoro_sessions[user_id].stop_pomodoro_session()
            del pomodoro_sessions[user_id]
            await bot.send_message(call.message.chat.id, f'Спринт отменен⛔')
        else:
            await bot.answer_callback_query(callback_query_id=call.id, text="У вас не запущен спринт")

    if call.data == "plus_work":
        current_minutes, _, _, _ = db.get_user_settings(user_id)
        if current_minutes == 45:
            db.update_working_minutes(user_id, 5)
        else:
            db.update_working_minutes(user_id, current_minutes + 5)
        await updated_settings(msg_with_settings, user_id)

    elif call.data == "minus_work":
        current_minutes, _, _, _ = db.get_user_settings(user_id)
        if current_minutes == 5:
            db.update_working_minutes(user_id, 45)
        else:
            db.update_working_minutes(user_id, current_minutes - 5)
        await updated_settings(msg_with_settings, user_id)

    elif call.data == "plus_break":
        _, current_short_break, current_long_break, _ = db.get_user_settings(user_id)
        if current_short_break == 15:
            db.update_break_minutes(user_id, 5)
            db.update_long_break_minutes(user_id, 15)
        else:
            db.update_break_minutes(user_id, current_short_break + 5)
            db.update_long_break_minutes(user_id, current_long_break + 5 * 3)
        await updated_settings(msg_with_settings, user_id)

    elif call.data == "minus_break":
        _, current_short_break, current_long_break, _ = db.get_user_settings(user_id)
        if current_short_break == 5:
            db.update_break_minutes(user_id, 15)
            db.update_long_break_minutes(user_id, 45)
        else:
            db.update_break_minutes(user_id, current_short_break - 5)
            db.update_long_break_minutes(user_id, current_long_break - 5 * 3)
        await updated_settings(msg_with_settings, user_id)

    elif call.data == "plus_cycles":
        _, _, _, current_cycles = db.get_user_settings(user_id)
        if current_cycles == 4:
            db.update_number_of_cycles(user_id, 1)
        else:
            db.update_number_of_cycles(user_id, current_cycles + 1)
        await updated_settings(msg_with_settings, user_id)

    elif call.data == "minus_cycles":
        _, _, _, current_cycles = db.get_user_settings(user_id)
        if current_cycles == 1:
            db.update_number_of_cycles(user_id, 4)
        else:
            db.update_number_of_cycles(user_id, current_cycles - 1)
        await updated_settings(msg_with_settings, user_id)


async def main():
    try:
        db.reset_timer_state_for_all_users()
        await dp.start_polling(bot)
    except Exception as e:
        if last_chat_id is not None:
            chat_id = await bot.get_chat(last_chat_id).id
            await bot.send_message(chat_id, f"Произошла ошибка: {e}\nОбратитесь в поддержку @fadeev16")
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
