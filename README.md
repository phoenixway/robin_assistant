# Robin AI
## About
Robin AI is artifical personal assistant. Project is in intersection of two domains - science/art of living and IT. For now as working prototype was devlopped in Python.

## Malware with same name
To my big and true sorry, malware with same name appeared in Internet in late 2022. Please be sure that it has nothing common with my Robin application. I don't know why that malware appeared and why it uses such a name, but my Robin is AI app which I started to delevop years ago. Since 2018. Name is dedicated to my friend - cat Robin. Just a coincidence.
 
## Features
* Communicate via text messages with Robin.
* Client/server architecure. Currently 2 protocols are supported: websockets and telegram (as bot).
* All Robin's behaviour in general including possible dialogs are described in the form of special story-files. 
* Story files have not-technician-friendly format.
* All Robin's behaviour in general including possible dialogs are described in the form of special story-files. Which have not-technician-friendly format.
* Не надто досліджував я мови скриптів інших чат-ботів, але щось мені підказує, що спосіб валідації вводу користувача та генерації відповіді на нього є достатньо іновативним.

## Installation
### Linux
Download source code:  
git clone https://github.com/phoenixway/robin_assistant  

Start virtual development enviroment:
python3 -m venv urname4enviroment
source urname4enviroment/bin/activate

Install requirements:  
pip3 install -r requirements.txt  

## Usage
Run 2 scripts (run_server.sh must be first) from {source code folder}/scripts in different terminals:  

scripts/run_server.sh  
scripts/run_client.sh  ## for gui client (buggy yet) OR  
scripts/run_client_cli.sh ## for cli client

## What next?
See TODO.md

## Licence
GNU 2

## Author
Roman Kozak (Pylypchuk)  
cossack.roman@gmail.com  
https://github.com/phoenixway  
https://twitter.com/roman_cossack  

2018-2023. Copyright Roman Kozak (Pylypchuk). All rights reserved.

