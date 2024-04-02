import asyncio

from timer import Timer


class Pomodoro:
    def __init__(self, user_id, work_minutes, short_break_minutes, long_break_minutes, cycles,
                 session_callback, break_callback, end_callback):
        self.is_stopped = False
        self.user_id = user_id
        self.work_minutes = work_minutes
        self.short_break_minutes = short_break_minutes
        self.long_break_minutes = long_break_minutes
        self.cycles = cycles
        self.session_callback = session_callback
        self.break_callback = break_callback
        self.end_callback = end_callback
        self.timers = []

    async def start_pomodoro_session(self):
        for cycle in range(self.cycles):
            work_timer = Timer(self.user_id, self.work_minutes, self.session_callback)
            break_timer = Timer(self.user_id, self.short_break_minutes, self.break_callback)
            long_break_timer = Timer(self.user_id, self.long_break_minutes, self.break_callback)

            self.timers.extend([work_timer, break_timer, long_break_timer])

            await work_timer.start()
            await asyncio.sleep(self.work_minutes * 60 + 1)
            if self.is_stopped:
                return
            if cycle != self.cycles - 1:
                await break_timer.start()
                await asyncio.sleep(self.short_break_minutes * 60 + 1)
                if self.is_stopped:
                    return
            else:
                await long_break_timer.start()
                await asyncio.sleep(self.long_break_minutes * 60 + 1)
                if self.is_stopped:
                    return

            self.timers.clear()
        if not self.is_stopped:
            await asyncio.sleep(1)
            await self.end_callback()

    def stop_pomodoro_session(self):
        self.is_stopped = True
        for timer in self.timers:
            timer.cancel()

    def time_remaining(self):
        if not self.timers:
            return None

        for timer in self.timers:
            if timer.is_running():
                return timer.get_remaining_time()

        return None
