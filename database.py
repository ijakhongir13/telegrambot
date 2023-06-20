# import sqlite3 as sq
#
# db = sq.connect('uzhydromet.db')
# cur = db.cursor()

import psycopg2

db = psycopg2.connect(
    host="localhost",
    database="uzhydromet",
    user="postgres",
    password="postgres"
)
cur = db.cursor()


async def db_start():
    cur.execute("CREATE TABLE IF NOT EXISTS applications("
                "id SERIAL PRIMARY KEY,"
                "user_id BIGINT,"
                "user_name TEXT,"
                "user_contact TEXT,"
                "request_type TEXT,"
                "request_number BIGINT DEFAULT NULL,"
                "request_content TEXT,"
                "request_add TEXT DEFAULT NULL,"
                "request_add_type TEXT DEFAULT NULL,"
                "request_datetime TEXT)")
    db.commit()


async def add_application(state):
    async with state.proxy() as data:
        cur.execute("INSERT INTO applications (user_id, user_name, user_contact, request_type, request_number, "
                    "request_content, request_add, request_add_type, request_datetime)"
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (data['user_id'], data['user_name'], data['user_contact'], data['request_type'],
                     data['request_number'], data['request_content'], data['request_add'],
                     data['request_add_type'], data['request_datetime']))
        db.commit()


async def get_request_id(state):
    async with state.proxy() as data:
        cur.execute("SELECT id FROM applications WHERE user_id = %s ORDER BY id DESC LIMIT 1", (data['user_id'],))
        result = cur.fetchone()
        db.commit()
        if result:
            return result[0]
        else:
            return None


async def set_request_number(state):
    async with state.proxy() as data:
        cur.execute("UPDATE applications SET request_number = %s WHERE id = (SELECT id FROM applications "
                    "WHERE user_id = %s ORDER BY id DESC LIMIT 1)", (data['request_number'], data['user_id']))
        db.commit()


async def get_all_results(state):
    async with state.proxy() as data:
        cur.execute("SELECT * FROM applications WHERE request_number = %s AND user_id = %s",
                    (data['request_number'], data['user_id']))
        result = cur.fetchone()
        db.commit()
        if result:
            return result
        else:
            return None
