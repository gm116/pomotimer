import sqlite3
import time
from datetime import datetime, timedelta


class DataBase:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor = self.connection.cursor()

    def __enter__(self):
        return self

    def __exit__(self, ext_type, exc_value, traceback):
        self.cursor.close()
        if isinstance(exc_value, Exception):
            self.connection.rollback()
        else:
            self.connection.commit()
        self.connection.close()

    def user_exists(self, user_id: int):
        with self.connection:
            result = self.connection.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchall()
            return bool(len(result))

    def add_user(self, user_id: int):
        with self.connection:
            self.cursor.execute("INSERT INTO users (user_id, session_count, minutes) VALUES (?, ?, ?)",
                                (user_id, 0, 0))
            self.cursor.execute(
                "INSERT INTO settings (user_id, minutes, short_break, long_break, cycles, timer_state)"
                "VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, 25, 5, 15, 4, 0))

    def get_numbers_of_sessions(self, user_id: int):
        with self.connection:
            result = self.connection.execute("SELECT session_count FROM users WHERE user_id = ?",
                                             (user_id,)).fetchone()
            if result is not None:
                return result[0]
            return None

    def get_numbers_of_minutes(self, user_id: int):
        with self.connection:
            result = self.connection.execute("SELECT minutes FROM users WHERE user_id = ?",
                                             (user_id,)).fetchone()
            if result is not None:
                return result[0]
            return None

    def get_stats_per_week(self, user_id: int):
        with self.connection:
            self.cursor.execute(
                "SELECT date, SUM(session_count) FROM weekly_stats WHERE user_id = ? "
                "AND date >= date('now','-7 day') GROUP BY date ORDER BY date",
                (user_id,))
            return self.cursor.fetchall()

    def get_stats_per_hour(self, user_id: int):
        with self.connection:
            self.delete_old_records_hourly()
            self.cursor.execute(
                "SELECT hour, session_count FROM hourly_stats WHERE user_id = ? "
                "AND hour >= date('now') ORDER BY hour",
                (user_id,))
            return self.cursor.fetchall()

    def delete_old_records_weekly(self):
        with self.connection:
            current_date = datetime.now().date()
            limit_date = current_date - timedelta(days=8)
            self.connection.execute(
                "DELETE FROM weekly_stats WHERE date < ?",
                (limit_date.strftime('%Y-%m-%d'),)
            )

    def get_user_settings(self, user_id: int):
        with self.connection:
            result = self.connection.execute(
                "SELECT minutes, short_break, long_break, cycles "
                "FROM settings WHERE user_id = ?",
                (user_id,)).fetchone()
        if result:
            return result[0], result[1], result[2], result[3]
        else:
            return None, None, None, None

    def update_working_minutes(self, user_id: int, minutes: int):
        with self.connection:
            self.connection.execute("UPDATE settings SET minutes = ? WHERE user_id = ?",
                                    (minutes, user_id))

    def update_break_minutes(self, user_id: int, break_minutes: int):
        with self.connection:
            self.connection.execute("UPDATE settings SET short_break = ? WHERE user_id = ?",
                                    (break_minutes, user_id))

    def update_long_break_minutes(self, user_id: int, long_break_minutes: int):
        with self.connection:
            self.connection.execute("UPDATE settings SET long_break = ? WHERE user_id = ?",
                                    (long_break_minutes, user_id))

    def update_number_of_cycles(self, user_id: int, cycles: int):
        with self.connection:
            self.connection.execute("UPDATE settings SET cycles = ? WHERE user_id = ?",
                                    (cycles, user_id))

    def delete_old_records_hourly(self):
        with self.connection:
            yesterday = datetime.now().date() - timedelta(days=1)
            yesterday_str = yesterday.strftime('%Y-%m-%d')
            yesterday_start_str = yesterday_str + ' 23:59:00'
            self.connection.execute(
                "DELETE FROM hourly_stats WHERE hour <= ?",
                (yesterday_start_str,)
            )

    def update_weekly_stats(self, user_id: int):
        with self.connection:
            date = time.strftime('%Y-%m-%d')
            self.cursor.execute("SELECT session_count FROM weekly_stats "
                                "WHERE user_id = ? AND date = ?",
                                (user_id, date))
            result = self.cursor.fetchone()
            if result is None:
                self.cursor.execute("INSERT INTO weekly_stats (user_id, date, session_count) "
                                    "VALUES (?, ?, ?)",
                                    (user_id, date, 1))
            else:
                session_count = result[0] + 1
                self.cursor.execute("UPDATE weekly_stats SET session_count = ? "
                                    "WHERE user_id = ? AND date = ?",
                                    (session_count, user_id, date))
            self.delete_old_records_weekly()

    def update_minutes(self, user_id: int, minutes: int):
        with self.connection:
            self.cursor.execute("UPDATE users SET minutes = minutes + ? WHERE user_id = ?",
                                (minutes, user_id))

    def update_hourly_stats(self, user_id: int):
        with self.connection:
            hour = time.strftime('%Y-%m-%d %H:00:00')
            self.cursor.execute("SELECT session_count FROM hourly_stats "
                                "WHERE user_id = ? AND hour = ?",
                                (user_id, hour))
            result = self.cursor.fetchone()
            if result is None:
                self.cursor.execute("INSERT INTO hourly_stats (user_id, hour, session_count) "
                                    "VALUES (?, ?, ?)",
                                    (user_id, hour, 1))
            else:
                self.cursor.execute(
                    "UPDATE hourly_stats SET session_count = session_count + 1 "
                    "WHERE user_id = ? AND hour = ?",
                    (user_id, hour))
            self.delete_old_records_hourly()

    def update_stats(self, user_id: int, minutes):
        with self.connection:
            self.update_minutes(user_id, minutes)
            self.cursor.execute("UPDATE users SET session_count = session_count + 1 "
                                "WHERE user_id = ?",
                                (user_id,))
            self.update_weekly_stats(user_id)
            self.update_hourly_stats(user_id)

    def get_timer_state(self, user_id: int):
        with self.connection:
            result = self.connection.execute(
                "SELECT timer_state FROM settings WHERE user_id = ?", (user_id,)
            ).fetchone()
            if result:
                return bool(result[0])
            return None

    def update_timer_state(self, user_id: int, state: int):
        with self.connection:
            self.connection.execute(
                "UPDATE settings SET timer_state = ? WHERE user_id = ?",
                (state, user_id)
            )

    def reset_timer_state_for_all_users(self):
        with self.connection:
            users = self.connection.execute("SELECT user_id FROM users").fetchall()
            for user in users:
                user_id = user[0]
                self.update_timer_state(user_id, 0)
