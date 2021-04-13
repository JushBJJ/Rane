# Rane Chat Client

![image](https://user-images.githubusercontent.com/36951064/114356224-b4d15100-9bb3-11eb-9dd7-22f5301016a3.png)

Rane is a chat client aimed to solve the issue of _______ _________ chat client websites. Therefore, this web application is to be ______ _______.

## How to setup

### Install Requirements

  `pip install -r requirements.txt`

### Generate Database [/tools]

  `python create_database`

### Change utils/rss.py IP connection

   `rss_socket.connect("http://192.
    168.1.10:5001/")`

   to

   `rss_socket.connect("http://YOUR_IP_HOST_AND_PORT/")`

    

### Run Server [/]
  `python run.py`

## Roadmap

- [x] Fully Transition to SQL
  - [x] Register
- [x] Create python script to generate database.
- [ ] Reorganize and comment repository code.
  - [ ] Reorganizing Functions
  - [ ] Function argument types defined
  - [ ] Commenting/Documenting
  - [ ] Removing unused imports
- [ ] Database Logging
- [ ] Encryption and security upgrades
