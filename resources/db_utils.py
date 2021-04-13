import sqlite3
import os
from sqlite3.dbapi2 import DatabaseError
from typing import Tuple

# TODO Think about unit testing for this.


def db_edit(filename, folder, function):
    def wrapper(*args, **kwargs):
        path = correct_path(folder, filename)

        try:
            db = sqlite3.connect(path)
        except DatabaseError as e:
            print(e)
            raise

        cursor = db.cursor()
        ret = function(cursor)
        cursor.close()

        db.commit()
        db.close()

        return ret

    return wrapper()


def correct_path(folder, filename):
    data = os.path.dirname(os.path.abspath(__file__))+"/../data/"
    path = data+folder+"/"+filename
    path__ = data+folder

    if os.path.exists(path__):
        return path
    else:
        return data+filename


def db_insert(cursor: sqlite3.Cursor, table: str, columns: str, values: str, unique: bool = False):
    try:
        # Check if value in table
        if unique:
            retrieve = db_retrieve(cursor, table, f"{columns}", f"{columns}={values}")
            if type(retrieve) == list:
                if len(retrieve) > 0:
                    for username in retrieve:
                        user = values.split("\"")
                        try:
                            if user[1] == username:
                                return True
                        except IndexError:
                            if user[0] == username:
                                return True
            else:
                return False

        cursor.execute(f"INSERT INTO {table} ({columns}) VALUES ({values})")
        return True
    except Exception as e:
        if not unique:
            # TODO Logging
            return False
        else:
            return True


def db_retrieve(cursor: sqlite3.Cursor, table: str, select: str, where: str):
    if where == "":
        ret = cursor.execute(f"SELECT {select} FROM {table}")
    else:
        try:
            ret = cursor.execute(f"SELECT {select} FROM {table} WHERE {where}")
        except sqlite3.OperationalError as e:
            print(e)
            print(f"SELECT {select} FROM {table} WHERE {where}")
            raise e
    return ret.fetchall()


def db_retrieve_all(cursor: sqlite3.Cursor, table: str):
    ret = cursor.execute(f"SELECT * FROM {table}")
    return ret.fetchall()


def db_update(cursor: sqlite3.Cursor, table: str, set_values: str, where: str):
    try:
        cursor.execute(f"UPDATE {table} SET {set_values} WHERE {where}")
        return True
    except Exception as e:
        print("Error: ", e)
        return False


def db_truncate(cursor, table: str):
    try:
        cursor.execute(f"DELETE FROM {table}")
        return True
    except Exception as e:
        print(e)
        return False


def db_delete(cursor, table: str, where: str):
    try:
        cursor.execute(f"DELETE FROM {table} WHERE {where}")
        return True
    except Exception as e:
        print(e)
        return False
