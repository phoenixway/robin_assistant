#!/usr/bin/env python3

import asyncio
from pathlib import Path
import logging
from yapsy.PluginManager import PluginManager

log = logging.getLogger('pythonConfig')
tsks = set()


class Plugins:

    def __init__(self, modules):
        self.MODULES = modules

    async def activate(self):
        log.debug("Plugin manager started.")
        global tsks
        simplePluginManager = PluginManager()
        source_path = Path(__file__).resolve()
        source_dir = source_path.parent / "plugins"
        simplePluginManager.setPluginPlaces([source_dir])
        simplePluginManager.collectPlugins()
        for pluginInfo in simplePluginManager.getAllPlugins():
            t = asyncio.create_task(pluginInfo.plugin_object.activate(
                self.MODULES))
            tsks.add(t)
