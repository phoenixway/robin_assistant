#!/usr/bin/env python3
import asyncio
import shelve
from time import sleep
from simple_websocket_server import WebSocketServer, WebSocket
from datetime import datetime
from icecream import ic
from multiprocessing import Process, Queue
db = shelve.open('spam')
#del db['dayplanned']
import websockets

MODULES = dict()

no_error = True

class Ws_server:
    async def say(self, message):
        global no_error
        if no_error and self.websocket:
            try:
                await self.websocket.send(message)
                print(f">>> {message}")
            except websockets.exceptions.ConnectionClosedOK:
                ic('ConnectionClosedOK')
                no_error = False

    async def echo(self, websocket):
        global no_error, MODULES
        self.websocket = websocket
        while no_error:
            try:
                name = await websocket.recv()
                print(f"<<< {name}")
                greeting = f"Hello {name}!"
                await websocket.send(greeting)
                print(f">>> {greeting}")
            except websockets.exceptions.ConnectionClosedOK:
                ic('ConnectionClosedOK')
                no_error = False

    async def ws_handle(self):
        await websockets.serve(self.echo, "localhost", 8765)
        await asyncio.Future()  # run forever

class Watcher:
    async def watch(self):
        while True:
            await asyncio.sleep(10)
            ic("im watch")
            await MODULES['ws_server'].say('Tada!')

watcher = Watcher()
ws_server = Ws_server()

MODULES['watcher'] = watcher
MODULES['ws_server'] = ws_server

async def main():
    results = await asyncio.gather(ws_server.ws_handle(), watcher.watch())
    ic(results)

asyncio.run(main())