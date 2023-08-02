#!/usr/bin/env python3

import sys
import os
import readline
import asyncio
import queue
import ssl
import threading
from abc import ABC, abstractmethod
from typing import Dict

import websockets
import nest_asyncio
from termcolor import colored
import aioconsole


nest_asyncio.apply()
is_input = False


queue = asyncio.Queue()
tasks = []
headers = dict
outgoing = asyncio.Queue()



class Suspendable:
    def __init__(self, target):
        self._target = target
        self._can_run = asyncio.Event()
        self._can_run.set()
        self._task = asyncio.ensure_future(self)

    def __await__(self):
        target_iter = self._target.__await__()
        iter_send, iter_throw = target_iter.send, target_iter.throw
        send, message = iter_send, None
        # This "while" emulates yield from.
        while True:
            # wait for can_run before resuming execution of self._target
            try:
                while not self._can_run.is_set():
                    yield from self._can_run.wait().__await__()
            except BaseException as err:
                send, message = iter_throw, err

            # continue with our regular program
            try:
                signal = send(message)
            except StopIteration as err:
                return err.value
            else:
                send = iter_send
            try:
                message = yield signal
            except BaseException as err:
                send, message = iter_throw, err

    def suspend(self):
        self._can_run.clear()

    def is_suspended(self):
        return not self._can_run.is_set()

    def resume(self):
        self._can_run.set()

    def get_task(self):
        return self._task

async def ainput(string: str) -> str:
    # await asyncio.get_event_loop().run_in_executor(
    #        None, lambda s=string: sys.stdout.write(s+' '))
    return await asyncio.get_event_loop().run_in_executor(
            None, sys.stdin.readline)


        # m = colored('Robin>', "yellow")
        # m1 = colored('You>', 'blue')
        # global is_input
        # if is_input:
            # pass
            # is_input = False
            # print("TRUE\n")
        # print(f"{m} {message} ")
        # print(f"{m1} ", end="")
        # print(f"{m} {message}{m1} ", end="") 


class Client:
    def __init__(self):
        self.is_input = False
        self.queue = asyncio.Queue()
        self.tasks = []
        self.headers = {}
        self.outgoing = asyncio.Queue()
        self.read_task = None

    async def write(self):
        while True:
            if self.queue.empty():
                await asyncio.sleep(0.5)
            else:
                try:
                    msg = self.queue.get(block=False)
                    print(f"{msg}")
                except self.queue.Empty:
                    continue


    async def handle_message(self, message):
        self.read_task.cancel()
        # sys.stdout.write(f"\nRobin>{message}" )
        # sys.stdout.flush()
        m = colored('Robin>', "yellow")
        print(f"\n{m}{message}")
        self.read_task = asyncio.create_task(self.read())

    async def listen_ingoing(self, socket):
        try:
            async for msg in socket:
                asyncio.create_task(self.handle_message(msg))
        except:
            print("\nBye")
            os._exit(1)

    async def listen_outgoing(self, socket):
        while True:
            if self.outgoing.empty():
                await asyncio.sleep(0.5)
            else:
                try:
                    msg = await self.outgoing.get()
                    asyncio.create_task(socket.send(msg))
                except queue.Empty:
                    continue
                    self.is_input = True
                except  Exception as e:
                    print(e)

    async def ws_client(self):
        url = 'ws://localhost:8765'
        try:
            async with websockets.connect(url, extra_headers=self.headers) as socket:
                task1 = self.listen_ingoing(socket)
                task2 = self.listen_outgoing(socket)
                await asyncio.gather(task1, task2)
        except e as Exception:
            print(f"{e} \nBye")
            # os._exit(1)
        print("end of wsclient")


    async def send(self):
        print("sended")
        #self.outgoing.put_nowait()
        # await self.write()

    async def read(self):
        c = True
        while True:
            m1 = colored('You>', 'green')
            text = await aioconsole.ainput(m1) 
            self.outgoing.put_nowait(text)
            self.read_task.cancel()

    async def arun(self):
        loop = asyncio.get_event_loop()
        self.read_task = loop.create_task(self.read())
        loop.create_task(self.ws_client())
        loop.create_task(self.write())
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            pass


def run():
    c = Client()
    asyncio.get_event_loop().run_until_complete(c.arun())


if __name__ == '__main__':
    run()
