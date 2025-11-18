import psycopg2
from psycopg2 import pool
from .config_loader import Config

class DatabasePool:
    _pool = None

    @classmethod
    def initialize(cls):
        if cls._pool is None:
            cls._pool = psycopg2.pool.SimpleConnectionPool(
                1, 10,
                dbname=Config.get('dbname'),
                user=Config.get('user'),
                password=Config.get('password'),
                host=Config.get('host'),
                port=Config.get('port')
            )

    @classmethod
    def get_conn(cls):
        if cls._pool is None:
            raise Exception("Connection pool not initialized.")
        return cls._pool.getconn()

    @classmethod
    def put_conn(cls, conn):
        if cls._pool:
            cls._pool.putconn(conn)

    @classmethod
    def close_all(cls):
        if cls._pool:
            cls._pool.closeall()