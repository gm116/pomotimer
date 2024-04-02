import asyncio
import time


class Timer:
    def __init__(self, user_id, minutes, callback):
        self.task = None
        self.user_id = user_id
        self.minutes = minutes
        self.callback = callback
        self.remaining_time = self.minutes * 60
        self.paused = False
        self.cancelled = False

    async def _timer_thread(self):
        start_time = time.time()
        while self.remaining_time > 0:
            if self.cancelled:
                return
            if not self.paused:
                elapsed_time = time.time() - start_time
                self.remaining_time = max(0, self.minutes * 60 - elapsed_time)
            await asyncio.sleep(1)
        if not self.cancelled:
            await self.callback()

    async def start(self):
        self.task = asyncio.create_task(self._timer_thread())

    def cancel(self):
        self.cancelled = True
        if hasattr(self, 'task') and self.task:
            self.task.cancel()

    def get_remaining_time(self):
        return round(self.remaining_time) // 61 + 1

    def is_running(self):
        return self.task and not self.task.done()
