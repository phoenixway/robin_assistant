import asyncio
import queue
import logging
import enum

log = logging.getLogger('pythonConfig')
background_tasks = set()

ActionType = enum.Enum(
    value="ActionType",
    names= ("SystemCommand SendMessage RespondToUserMessage"),
)

class Action:
    def __init__(self, action_type: ActionType, value: str):
        self.value = value
        self.action_type = action_type


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
                    if a.action_type == ActionType.RespondToUserMessage:
                        self.respond_to_user_message_callback(text=a.value)
                    elif a.action_type == ActionType.SendMessage:
                        log.debug(f'Sended message: {a.value}')
                        self.send_message_callback(a.value)
                    elif a.action_type == ActionType.SystemCommand:
                        log.debug(f'Received system command: {a.value}')
                        match a.value:
                            case ":force_own_will":
                                self.force_own_will_callback()
                            case ":close_server":
                                self.close_server_callback()
                            case ":close":
                                raise Exception("Client connection closing is not implemented yet")
                                # self.close_client_callback()
                            case _:
                                pass
                        self.send_message_callback(a.value)
                except queue.Empty:
                    continue
                except Exception as e:
                    log.error(e)
                    log.debug("Closing server and client because of exception..")
                    self.close_server_callback()
    
    def add_action(self, a: Action) -> None:
        """Add an action to the queue"""
        self.queue.put_nowait(a)
