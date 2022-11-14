#!/usr/bin/env bash
# -*- coding: utf-8 -*
cd /home/roman/Projects/robin_assistant/ws_chat/vue_chat || exit
yarn build
cd ..
neu build
cd /home/roman/Projects/robin_assistant || exit
/home/roman/Projects/robin_assistant/ws_chat/dist/ws_chat/ws_chat-linux_x64
