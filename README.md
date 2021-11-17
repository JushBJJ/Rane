# Rane Chat Client

![image](https://user-images.githubusercontent.com/36951064/114356224-b4d15100-9bb3-11eb-9dd7-22f5301016a3.png)

Rane is a chat client aimed to solve the issue of _______ _________ chat client websites. Therefore, this web application is to be ______ _______.

## It doesn't work!
It works on my machine.
## How to setup

### Install Requirements

    pip install -r requirements.txt

### Generate Database [/tools]

    python create_database

### Run Server (Main File)[/]
    python run.py

The server will be hosted in your localhost ip. (eg. http://192.168.1.10:5000)
## Roadmap

- [x] Fully Transition to SQL
  - [x] Register
- [x] Create python script to generate database.
- [x] Reorganize and message repository code.
  - [x] Reorganizing Functions
  - [x] Function argument types defined
  - [x] Commenting code.
  - [x] Removing unused imports and reordered imports
- [ ] Security
  - [ ] Fix SQL injection vulnrelability.
  - [ ] Encryption
    - [ ] Database
    - [ ] Websocket access
