import asyncio
import queue
import logging

log = logging.getLogger('pythonConfig')
background_tasks = set()

class Action:
    pass


class SendMessageAction(Action):
    def __init__(self, message : str ) -> None:
        self.message = message
        super().__init__()


class RespondToUserMessageAction(Action):
    def __init__(self, message : str ) -> None:
        self.message = message
        super().__init__()
        

class ActionsQueue:
    def __init__(self) -> None:
        self.queue = asyncio.Queue()
        self.send_message_callback = None
        self.respond_to_user_message_callback = None
            
    async def listen_queue(self):
        while True: 
            if self.queue.empty():
                await asyncio.sleep(0.2)
            else:
                try:
                    a = await self.queue.get()
                    if isinstance(a, RespondToUserMessageAction):
                        callback=self.respond_to_user_message_callback(a.message)
                    elif isinstance(a, SendMessageAction):
                        callback=self.send_message_callback(a.message)
                except queue.Empty:
                    continue
                except  Exception as e:
                    log.error(e)
    
    def add_action(self, a: Action) -> None:
        """Add an action to the queue"""
        self.queue.put_nowait(a)