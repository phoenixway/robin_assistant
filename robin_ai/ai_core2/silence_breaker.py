import asyncio
import logging  
import nest_asyncio


nest_asyncio.apply()
log = logging.getLogger('pythonConfig')
tasks = set()

class SilenceBreaker:
    def __init__(self, debug = False):
        self.silence_task = None
        self.handle_silence = True
        self.silence_breaker_callback = None
        if debug:
            self.set_silence_time(seconds=5)
        else:
            self.set_silence_time(minutes=2)
    
    async def start_silence_async(self):
        log.debug("Silence detection started")
        log.debug(f"Waiting silence for {self.silence_time} seconds")
        await asyncio.sleep(self.silence_time)
        log.debug("Silence detected")
        if self.silence_breaker_callback:
            self.silence_breaker_callback()

    def get_loop(self):
        l = None
        try:
            l = asyncio.get_running_loop()
        except RuntimeError:
            l = None

        if l is None or not (l.is_running()):
            l = asyncio.new_event_loop()
            asyncio.set_event_loop(l)
        return l
    
    def start_silence(self):
        while self.handle_silence:
            try:
                if not self.handle_silence:
                    return
                if self.silence_task is not None:
                    self.silence_task.cancel()
                self.silence_task = self.get_loop().create_task(self.start_silence_async())
                tasks.add(self.silence_task)
            except Exception as e:
                log.error(e)

    def set_silence_time(self, minutes=0, seconds=0):
        self.silence_time = minutes * 60 + seconds