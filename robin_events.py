#!/usr/bin/env python3

from events import Events
class Robin_events(Events):
    __events__ = ('on_startup', 'on_connected', 'on_quit')