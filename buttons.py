from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

START_PROMPT = "Привет! 👋 Я телеграм-бот ПомоТаймер! 🍅\n\n" \
               "Я помогу вам улучшить продуктивность и организовать ваше время с помощью методики Помодоро 📝\n\n" \
               "Методика Помодоро - это простой и эффективный способ управления временем и повышения продуктивности. Она основана на разделении рабочего времени на интервалы продолжительностью 25 минут, называемые помидорами, за которыми следует короткий перерыв. После каждых четырех помидоров делается длинный перерыв.\n\n" \
               "Для начала работы, вы можете поставить таймер на определенное время, чтобы сосредоточиться на задаче. Просто нажмите на кнопку \"Поставить таймер\" и выберите продолжительность вашего работы ⏰\n\n" \
               "Если вы готовы приступить к спринту, который включает в себя несколько помидоров работы и перерывов, нажмите на кнопку \"Запустить спринт\" 🚀\n\n" \
               "Настройте количество сессий, длительность работы и отдыха так, как тебе удобно, и начинайте работать над своими задачами! 🛠️\n\n" \
               "Не забывайте делать короткие перерывы после каждого помидора и длинные перерывы после четырех помидоров, чтобы поддерживать свою энергию и концентрацию ☕️\n\n" \
               "Успешной и продуктивной работы! 💪🕒"


def start():
    markup = [
        [KeyboardButton(text='Поставить таймер ⏲️'),
         KeyboardButton(text='Запустить спринт 🚀')],
        [KeyboardButton(text='Отобразить статистику 📊'),
         KeyboardButton(text='Настроить спринт ⚙️')]
    ]
    return ReplyKeyboardMarkup(keyboard=markup, resize_keyboard=True)


def pomodoro():
    markup = [
        [InlineKeyboardButton(text='5 минут 🕐', callback_data='5')],
        [InlineKeyboardButton(text='15 минут 🕑', callback_data='15')],
        [InlineKeyboardButton(text='25 минут 🕒', callback_data='25')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=markup)


def stats():
    markup = [
        [InlineKeyboardButton(text='Количество минут и завершенных сессий 📈', callback_data='info_stats')],
        [InlineKeyboardButton(text='Отобразить график за неделю 📊', callback_data='weekly_stats')],
        [InlineKeyboardButton(text='Отобразить график за сегодня 📊', callback_data='hourly_stats')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=markup)


def active_timer():
    markup = [
        [InlineKeyboardButton(text='Узнать сколько осталось времени ⏳', callback_data='time_left')],
        [InlineKeyboardButton(text='Остановить таймер ⏹️', callback_data='stop_timer')],
    ]
    return InlineKeyboardMarkup(inline_keyboard=markup)


def active_sprint():
    markup = [
        [InlineKeyboardButton(text='Узнать сколько осталось времени ⏳', callback_data='sprint_left')],
        [InlineKeyboardButton(text='Остановить спринт ⏹️', callback_data='stop_sprint')],
    ]
    return InlineKeyboardMarkup(inline_keyboard=markup)


def settings():
    markup = [
        [InlineKeyboardButton(text='+💼', callback_data='plus_work'),
         InlineKeyboardButton(text='+⏳', callback_data='plus_break'),
         InlineKeyboardButton(text='+🍅', callback_data='plus_cycles')],
        [InlineKeyboardButton(text='-💼', callback_data='minus_work'),
         InlineKeyboardButton(text='-⏳', callback_data='minus_break'),
         InlineKeyboardButton(text='-🍅', callback_data='minus_cycles')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=markup)
