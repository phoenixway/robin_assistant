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

clients = []
messanger = None
server_global = None

def say(message):
    for client in clients:
        client.send(message)
        ic()

class JustChat(WebSocket):
    def broadcast(self, message):
        for client in clients:
            client.send_message(message)

    def say(self, message):
        for client in clients:
            client.send_message(message)

    def handle(self):
        for client in clients:
            # if client != self:
            if self.data == 'day planned':
                dt = datetime.today().strftime('%Y-%m-%d')
                db['dayplanned'] = dt   
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
        global messanger 
        messanger = self
        pass

    def handle_close(self):
        clients.remove(self)
        print(self.address, 'closed')
        for client in clients:
            client.send_message(self.address[0] + u' - disconnected')


def ws_handler(queue):
    ic('server connected')
    server = WebSocketServer('', 8765, JustChat)
    queue.put(server)
    server.serve_forever()

async def queue_handler():
    pass

def watch_params(queue):
    print('watch_params')
    while True:
        sleep(10)
        dt = datetime.today().strftime('%Y-%m-%d')
        if not db.get('dayplanned') or db.get('dayplanned') != dt:
            m = "You did not plan your day!"
            ic(m)
            server = queue.get()

            # ic(server.clients)
            say(m)
            ic()

async def main():
    #task1 = asyncio.create_task(ws_handler())
    #task2 = asyncio.create_task(queue_handler())
    task3 = asyncio.create_task(watch_params())
    await task3
    # await task1
    # #await task2
    # await task3
q = Queue()
processes = []
proc = Process(target=ws_handler, args=(q,))
proc.start()
processes.append(proc)
proc1 = Process(target=watch_params, args=(q,))
proc1.start()
processes.append(proc1)
try:
    #asyncio.run(main())
    pass
except KeyboardInterrupt:
    pass
finally:
    db.close()
    for proc in processes:
        proc.join()