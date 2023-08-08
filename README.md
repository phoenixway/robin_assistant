# Robin AI
## About
Robin AI is artifical personal assistant. Project is in intersection of two domains - science/art of living and IT. For now as working prototype was developed in Python.

## Features
* Communicate with Robin in chat form via text messages.
* Client/server technical  architecure. For app to work it must be two running parts: server (app brains) and chat client (in future - in every platform).
* Currently 1 protocols are supported: websockets. Telegram as bot opt is freazed for now.
* All Robin's behaviour including possible dialogs are prescribed and described in the form of special format "story" files. 
* Story format is very not-technician-friendly. Fast to learn, use, improve.
* Answers are generated based on such a story files in an unique way, different from similar apps, with use Robin AI core.
 
## Future
* Multi user
* Multi platform.
* See TODO.md

## Motivation to develop and use
I like virtual assistant Tony Stark has in Iron Man. I think it is really cool to develop and use similar.

Most people will agree that modern human-machine interfaces are not natural way for human to process information and communicate. I want more intuitive, natural way. And fun. 

For me existing chat and AI engines have one crucial disadvantage: I can't quickly modify them if necessary. Robin-AI I can easy modify both engine and scripts. I (and any another user too) can write scripts for personal assistant very quickly. Practically with a speed of a writer of fiction with his text editor. You just have to take a little time and learn how to use it.

## Installation
### Linux
Download source code:                                                                   
```sh
git clone https://github.com/phoenixway/robin_assistant  
```

## Usage
For app to start run 2 scripts below (run_server.sh must be first) from {project folder}/scripts in different terminals: 

```sh
scripts/run_server.sh  ## server
scripts/run_client_cli.sh ## cli client
```
They will work in Linux, Macos and in WLS of Windows
 
For format of stories and plugins look at default.brains and default.plugins folders.
 
## Malware with same name
To my big and true sorry malware with same name appeared in Internet in late 2022. Please be sure that it has nothing common with my Robin application. I don't know why that malware appeared and why it uses such a name, but my Robin is AI app which I started to delevop since 2018. 

Name is dedicated to my friend - cat Robin. 
 
## License
GNU 2

## Author
Roman Kozak (Pylypchuk)  
cossack.roman@gmail.com  
https://github.com/phoenixway  
https://twitter.com/roman_cossack  

2018-2023. Copyright Roman Kozak (Pylypchuk). All rights reserved.

