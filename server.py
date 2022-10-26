#!/usr/bin/env python3

import asyncio
import websockets

async def echo(websocket):
    async for message in websocket:
        print(f"\n> {message}")
        await websocket.send(message)

async def websocket_handler():
    async with websockets.serve(echo, "localhost", 8765):
        await asyncio.Future()  # run forever


async def main():
    task_ws = asyncio.create_task(websocket_handler())
    await task_ws

asyncio.run(main())
