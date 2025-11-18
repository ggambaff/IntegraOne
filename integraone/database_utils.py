# -*- coding: utf-8 -*-
import logging
import psycopg2
from integraone.config_loader import Config

_logger = logging.getLogger(__name__)

import psycopg2
import logging

_logger = logging.getLogger(__name__)

def ensure_database_exists():
    dbname = Config.get("dbname")
    user = Config.get("user")
    password = Config.get("password")
    host = Config.get("host")
    port = Config.get("port")

    # Conexión a la base de datos postgres para verificar/crear la base de datos
    conn = psycopg2.connect(
        dbname="postgres",
        user=user,
        password=password,
        host=host,
        port=port
    )
    conn.autocommit = True

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (dbname,))
            exists = cur.fetchone()
            if not exists:
                _logger.info("La base de datos '%s' no existe. Creando...", dbname)
                cur.execute(f"CREATE DATABASE {dbname};")
            else:
                _logger.info("La base de datos '%s' ya existe", dbname)
    finally:
        conn.close()

    # Conexión a la base de datos recién creada para crear la tabla
    conn_db = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )
    conn_db.autocommit = True

    try:
        with conn_db.cursor() as cur:
            # Aquí defines tu tabla, por ejemplo:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS system_users (
                    id SERIAL PRIMARY KEY
                );
            """)
            _logger.info("Table 'system_users' verified/created in database '%s'", dbname)
    finally:
        conn_db.close()

def ensure_base_exists():
    dbname = Config.get("dbname")
    user = Config.get("user")
    password = Config.get("password")
    host = Config.get("host")
    port = Config.get("port")

    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )
    conn.autocommit = True

    try:
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT EXISTS (SELECT
                                       FROM information_schema.tables
                                       WHERE table_schema = 'public'
                                         AND table_name = %s);
                        """, ("base_module_list",))

            exists = cur.fetchone()[0]
            if exists:
                _logger.info("The base modules are created")
                return True
            else:
                _logger.info("The base modules are not created")
                return False
    finally:
        conn.close()