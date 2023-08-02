#!/usr/bin/env bash
SOURCE=${BASH_SOURCE[0]}
DIR=$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )
cd $DIR/../client4robin
python setup.py sdist && pex aioconsole nest_asyncio termcolor websockets client4robin -o client_cli.pex -f dist -e client4robin.client --disable-cache 
