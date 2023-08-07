#!/usr/bin/env bash
SOURCE=${BASH_SOURCE[0]}
DIR=$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )
cp ~/.config/robin_assistant/plugins/* ~/studio/offline🏡/robin_assistant/robin_ai/default_plugins/
cp ~/.config/robin_assistant/brains/* ~/studio/offline🏡/robin_assistant/robin_ai/default_brains/
cd $DIR/../
python setup.py sdist 
pex -r requirements.txt robin_assistant  -o robin_server.pex -f dist --disable-cache -e robin_ai.robin_ai:main 
