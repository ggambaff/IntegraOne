import psycopg2
from psycopg2 import pool

class DatabasePool:
    _pool = None

    @classmethod
    def initialize(cls, minconn=1, maxconn=10, **db_params):
        """
        Inicializa el pool de conexiones con los parámetros de conexión.
        """
        if cls._pool is None:
            try:
                cls._pool = pool.SimpleConnectionPool(
                    minconn=minconn,
                    maxconn=maxconn,
                    **db_params
                )
                print("✅ Pool de conexiones inicializado correctamente.")
            except Exception as e:
                raise Exception(f"Error al inicializar el pool de conexiones: {e}")

    @classmethod
    def get_connection(cls):
        """
        Obtiene una conexión del pool.
        """
        if cls._pool is None:
            raise Exception("El pool de conexiones no ha sido inicializado.")
        try:
            return cls._pool.getconn()
        except Exception as e:
            raise Exception(f"No se pudo obtener una conexión del pool: {e}")

    @classmethod
    def release_connection(cls, conn):
        """
        Devuelve la conexión al pool.
        """
        if cls._pool is None:
            raise Exception("El pool de conexiones no ha sido inicializado.")
        try:
            cls._pool.putconn(conn)
        except Exception as e:
            raise Exception(f"No se pudo liberar la conexión al pool: {e}")

    @classmethod
    def close_all(cls):
        """
        Cierra todas las conexiones del pool.
        """
        if cls._pool:
            try:
                cls._pool.closeall()
                print("✅ Todas las conexiones del pool han sido cerradas.")
            except Exception as e:
                raise Exception(f"Error al cerrar las conexiones del pool: {e}")