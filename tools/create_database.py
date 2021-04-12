import sqlite3
import os
import shutil

path = "../data/"

# Create data folder and subdirectories
os.mkdir(path)
os.mkdir(path+"/keys/")
os.mkdir(path+"/rooms/")
os.mkdir(path+"/server/")

# Create Databases
databases = {
    "./room_template.db": ['''
        CREATE TABLE "Admins" (
        	"Username"	TEXT UNIQUE,
        	"ID"	INTEGER UNIQUE
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
        	"message"	TEXT,
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
    ''']
}

for database in databases.keys():
    db_path = path+database

    db = sqlite3.connect(db_path)

    cur = db.cursor()
    for command in databases[database]:
        cur.execute(command)

    cur.close()
    db.commit()


# Create Genesis Room
shutil.copyfile(path+"./room_template.db", path+"/rooms/0.db")
