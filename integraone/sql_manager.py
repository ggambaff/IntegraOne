import psycopg2
from psycopg2.extensions import connection as BaseConnection
from queue import Queue
from . import tools

# -------------------------------
# Clase personalizada: PsycoConnection
# -------------------------------
class PsycoConnection(BaseConnection):
    def cursor(self, *args, **kwargs):
        print("[LOG] Creando cursor...")
        return super().cursor(*args, **kwargs)

    def commit(self):
        print("[LOG] Commit ejecutado")
        super().commit()

    def rollback(self):
        print("[LOG] Rollback ejecutado")
        super().rollback()

# -------------------------------
# Clase: ConnectionPool
# -------------------------------
class ConnectionPool:
    def __init__(self, maxconn):
        self._pool = Queue(maxconn)
        self._db_params = db_params = tools
        for _ in range(maxconn):
            conn = psycopg2.connect(
                **db_params,
                connection_factory=PsycoConnection
            )
            self._pool.put(conn)

    def getconn(self):
        return self._pool.get()

    def putconn(self, conn):
        self._pool.put(conn)

    def closeall(self):
        while not self._pool.empty():
            conn = self._pool.get()
            conn.close()

# -------------------------------
# Clase: Connection
# -------------------------------
class Connection:
    def __init__(self, pool):
        self._pool = pool
        self._conn = pool.getconn()

    def cursor(self):
        return self._conn.cursor()

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        self._pool.putconn(self._conn)

# -------------------------------
# Función: db_connect
# -------------------------------
_Pool = None

def db_connect(config_path, allow_uri=False):
    global _Pool
    config = configmanager()
    db_params = config.parse_config(["-c", config_path])
    db = db_params.get("dbname")
    if not allow_uri and not db:
        raise ValueError('URI connections not allowed')
    if _Pool is None:
        _Pool = ConnectionPool(maxconn=5, db_params=db_params)
    return Connection(_Pool)