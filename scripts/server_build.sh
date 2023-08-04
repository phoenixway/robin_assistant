#!/usr/bin/env bash
SOURCE=${BASH_SOURCE[0]}
DIR=$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )
cd $DIR/../
python setup.py sdist 
pex -r requirements.txt robin_assistant  -o robin_server.pex -f dist --disable-cache -e robin_ai.robin_ai:main 
