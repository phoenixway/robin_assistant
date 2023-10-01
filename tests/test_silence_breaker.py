#!/usr/bin/env python3
import pytest
import logging
import asyncio 
import os, sys
import pytest_asyncio_cooperative.plugin


pytest_plugins = ('pytest_asyncio_cooperative')

sys.path.append(os.path.abspath('..'))
sys.path.append(os.path.abspath('../robin_ai'))
logging.basicConfig(level=logging.DEBUG)
logging.debug(os.getcwd())
logg = logging.getLogger('pythonConfig')
st = set()

from robin_ai.ai_core2.silence_breaker import SilenceBreaker, tasks

@pytest.mark.asyncio_cooperative
async def test_async_silence_breaker():
    called = False
    
    def callback():
        nonlocal called
        called = True
        
    sb = SilenceBreaker(debug = True)
    sb.silence_breaker_callback = callback
    sb.start_silence()
    await sb.start_silence_async()
    assert called, "Callback should be called"
    
def test_silence_breaker():
    called = False
    
    def callback():
        nonlocal called
        called = True
        
    sb = SilenceBreaker(debug = True)
    sb.silence_breaker_callback = callback
    sb.start_silence()
    assert sb.silence_task in tasks, "silence_task is not in silence_breaker.tasks"
    asyncio.run(sb.silence_task)
    assert called, "Callback should be called"
    