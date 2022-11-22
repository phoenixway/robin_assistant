#!/usr/bin/env python3

# from events import Events

import asyncio
background_tasks = set()
# got at https://github.com/joeltok/py-event-bus/blob/main/event_bus/EventBus.py


class Robin_events():
    def __init__(self):
        self.listeners = {}
        self.is_started = True

    def add_listener(self, event_name, listener):
        if not self.listeners.get(event_name, None):
            self.listeners[event_name] = {listener}
        else:
            self.listeners[event_name].add(listener)

    def remove_listener(self, event_name, listener):
        self.listeners[event_name].remove(listener)
        if len(self.listeners[event_name]) == 0:
            del self.listeners[event_name]

    def emit(self, event_name, event):
        listeners = self.listeners.get(event_name, [])
        for listener in listeners:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None
            if not loop or not loop.is_running():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            t = loop.create_task(listener(event))
            background_tasks.add(t)
