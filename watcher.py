#!/usr/bin/env python3

import asyncio
import logging
from yapsy.PluginManager import PluginManager

log = logging.getLogger('pythonConfig')
tsks = set()        # ai_core = self.MODULES['ai_core']


class Watcher:

    def __init__(self, modules):
        self.MODULES = modules

    async def watch(self):
        log.debug("I'm Watcher and I'm watching!")
        global tsks
        simplePluginManager = PluginManager()
        simplePluginManager.setPluginPlaces(["plugins"])
        simplePluginManager.collectPlugins()
        for pluginInfo in simplePluginManager.getAllPlugins():
            # simplePluginManager.activatePluginByName(pluginInfo.name)
            t = asyncio.create_task(pluginInfo.plugin_object.activate(self.MODULES))
            tsks.add(t)
        # while True:
        #     await asyncio.sleep(4)
