import sqlite3
import shutil
import os

path = "./data/"
logs = "./logs/"
uploads = "./static/uploads"

remove_folders = [path, logs, uploads]

for folder in remove_folders:
    if os.path.exists(folder):
        shutil.rmtree(folder)

# Create data folder and subdirectories
os.mkdir(path)
os.mkdir(path+"/keys/")
os.mkdir(path+"/rooms/")
os.mkdir(path+"/server/")
os.mkdir(logs)
os.mkdir(uploads)

# Create Databases
databases = {
    "./room_template.db": ['''
        CREATE TABLE "Members" (
        	"ID"	INTEGER UNIQUE,
        	"Username"	TEXT UNIQUE,
        	"Role"	TEXT
        );''', '''
        CREATE TABLE "Blacklisted" (
        	"Username"	TEXT UNIQUE,
        	"ID"	INTEGER UNIQUE
        );''', '''
        CREATE TABLE "Invites" (
        	"Code"	TEXT UNIQUE
        );''', '''
        CREATE TABLE "Messages" (
        	"message_id"	INTEGER,
        	"author_id"	INTEGER,
        	"author_ip"	TEXT,
        	"message"	TEXT NOT NULL,
            "media" TEXT NOT NULL,
        	"show"	INTEGER,
        	PRIMARY KEY("message_id" AUTOINCREMENT)
        );''', '''
        CREATE TABLE "Name" (
        	"Name"	TEXT
        );''', '''
        CREATE TABLE "Owners" (
        	"Username"	TEXT UNIQUE,
        	"ID"	INTEGER UNIQUE
        );''', '''
        CREATE TABLE "Whitelisted" (
        	"Username"	TEXT,
        	"ID"	INTEGER
        );'''],
    "./rooms.db": ['''
        CREATE TABLE "Rooms" (
        	"Name"	TEXT,
        	"Description"	TEXT,
        	"ID"	TEXT UNIQUE,
        	"Public"	INTEGER
        );
    '''],
    "./server_info.db": ['''
        CREATE TABLE "online" (
        	"username"	TEXT UNIQUE
        );
    '''],
    "./server/accounts.db": ['''
        CREATE TABLE "accounts" (
        	"username"	TEXT,
        	"password"	TEXT,
        	"ip"	TEXT,
        	"status"	TEXT,
        	"seen"	TEXT,
        	"id"	INTEGER UNIQUE,
        	"server role"	TEXT,
        	PRIMARY KEY("id" AUTOINCREMENT)
        );
    '''],
    "./server/admins.db": ['''
        CREATE TABLE "admins" (
    	    "username"	TEXT
        );
    
    '''],
    "./server/blacklist.db": ['''
        CREATE TABLE "blacklist" (
    	    "ip"	TEXT
        );
    '''],
}

for database in databases.keys():
    db_path = path+database

    db = sqlite3.connect(db_path)

    cur = db.cursor()
    for command in databases[database]:
        cur.execute(command)

    cur.close()
    db.commit()
    db.close()


# Create Genesis Room
shutil.copyfile(path+"./room_template.db", path+"/rooms/0.db")

db = sqlite3.connect(path+"./rooms/0.db")
cur = db.cursor()
cur.execute("INSERT INTO Name VALUES (\"Genesis\")")
cur.close()
db.commit()
db.close()

db = sqlite3.connect(path+"./rooms.db")
cur = db.cursor()
cur.execute('INSERT INTO Rooms (Name, Description, ID, Public) VALUES ("Genesis", "Founding Room", "0", 1)')
cur.close()
db.commit()
db.close()
