import logging, asyncio
from random import choice

log = logging.getLogger('pythonConfig')

def say_hello(modules):
    a = {"Hey", "Hello", "Glad to see you"}
    return str(choice(tuple(a)))

def you_planned_day(modules):
    return "You planned your day, congratulations!"

def you_planned_day2(modules):
    return "You make it!"

def say_bye(modules):
    log.debug('say_bye lanched')
    modules['events'].emit('quit', None)
    return "Good bye, master"

def answer_cursing(modules):
    a = {"Don't curse", "U like that..", "Please, stop that", "Watch your language, please"}
    return str(choice(tuple(a)))