python setup.py sdist 
pex -r requirements.txt robin_assistant  -o robin_server.pex -f dist --disable-cache -e robin_ai.robin_ai:main 