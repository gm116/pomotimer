from datetime import datetime, timedelta
import io
import matplotlib.pyplot as plt


def send_weekly_plot(result):
    dates, session_counts = zip(*result)
    dates = [datetime.strptime(date, '%Y-%m-%d') for date in dates]
    dates = [datetime.date(date) for date in dates]
    plt.figure(figsize=(10, 5))

    # Формируем диапазон дат за последние 7 дней
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=6)
    last_week_dates = [start_date + timedelta(days=i) for i in range(7)]

    data = []
    for date in last_week_dates:
        if date in dates:
            index = dates.index(date)
            data.append(session_counts[index])
        else:
            data.append(0)
    plt.grid(alpha=0.3)
    plt.bar(last_week_dates, data, color='skyblue', width=0.5)  # Увеличиваем ширину столбцов
    plt.title('Статистика за последние 7 дней')
    plt.xlabel('Дата')
    plt.ylabel('Количество сессий')

    # Сохраняем график в виде изображения в памяти
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return buf


def send_hourly_plot(result):
    hours, session_counts = zip(*result)
    hours = [datetime.strptime(hour, '%Y-%m-%d %H:%M:%S') for hour in hours]

    plt.figure(figsize=(10, 5))
    plt.grid(alpha=0.3)
    plt.bar(hours, session_counts, width=0.03, color='skyblue')  # Создаем гистограмму
    plt.title('Статистика по часам')
    plt.xlabel('Час')
    plt.ylabel('Количество сессий')
    plt.ylim(bottom=0)

    plt.xticks([datetime.now().replace(hour=i, minute=0) for i in range(24)],
               [f'{i:02d}' for i in range(24)])

    # Сохраняем график в виде изображения в памяти
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return buf
