from integraone.db import DatabasePool

def execute(query, params=None):
    conn = None
    try:
        conn = DatabasePool.get_conn()
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            conn.commit()
    finally:
        if conn:
            DatabasePool.put_conn(conn)

def fetch_all(query, params=None):
    conn = None
    try:
        conn = DatabasePool.get_conn()
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchall()
    finally:
        if conn:
            DatabasePool.put_conn(conn)