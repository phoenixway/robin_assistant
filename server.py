#!/usr/bin/env python3
import asyncio
from simple_websocket_server import WebSocketServer, WebSocket

class SimpleChat(WebSocket):
    def handle(self):
        for client in clients:
            # if client != self:
            answer = f"Echoing {self.data}"
            client.send_message(answer)
            # client.send_message(self.address[0] + u' - ' + self.data)
            print(self.address[0] + u'> ' + self.data)
            print(f"Me> {answer}")

    def connected(self):
        print(f"{self.address[1]} process from {self.address[0]} is connected. ")
        for client in clients:
            client.send_message(self.address[0] + u' - connected')
        clients.append(self)

    def handle_close(self):
        clients.remove(self)
        print(self.address, 'closed')
        for client in clients:
            client.send_message(self.address[0] + u' - disconnected')


clients = []

async def ws_handler():
    server = WebSocketServer('', 8765, SimpleChat)
    server.serve_forever()

async def queue_handler():
    pass

async def main():
    task1 = asyncio.create_task(ws_handler())
    task2 = asyncio.create_task(queue_handler())
    await task1
    await task2

try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass