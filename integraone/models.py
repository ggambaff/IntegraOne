# -*- coding: utf-8 -*-
from integraone.database_pool import DatabasePool
from integraone.fields import Field

class MetaModel(type):
    def __new__(cls, name, bases, attrs):
        fields = {}
        meta_attrs = {}

        for key, value in attrs.items():
            if isinstance(value, Field):
                fields[key] = value
            elif key.startswith('_'):
                meta_attrs[key] = value

        attrs['_fields'] = fields
        attrs['_meta'] = meta_attrs

        return super().__new__(cls, name, bases, attrs)

class Model(metaclass=MetaModel):
    def __init__(self, **kwargs):
        for field_name in self._fields:
            setattr(self, field_name, kwargs.get(field_name))

    @classmethod
    def create_table(cls):
        columns = []
        for name, field in cls._fields.items():
            columns.append(f"{name} {field.sql()}")
        table_name = cls._meta.get('_name', cls.__name__.lower())
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)});"
        cls._execute(query)

    def save(self):
        columns = ', '.join(self._fields.keys())
        values = ', '.join(['%s'] * len(self._fields))
        data = [getattr(self, key) for key in self._fields.keys()]
        table_name = self._meta.get('_name', self.__class__.__name__.lower())
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({values});"
        self._execute(query, data)

    @staticmethod
    def _execute(query, params=None):
        conn = None
        try:
            conn = DatabasePool.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(query, params or ())
                conn.commit()
        finally:
            if conn:
                DatabasePool.release_connection(conn)
    @staticmethod
    def parse_domain(domain):
        def to_sql(condition):
            field, operator, value = condition
            if operator.upper() in ['IS NULL', 'IS NOT NULL']:
                return f"{field} {operator}", []
            elif operator.upper() == 'IN' and isinstance(value, (list, tuple)):
                placeholders = ', '.join(['%s'] * len(value))
                return f"{field} IN ({placeholders})", list(value)
            else:
                return f"{field} {operator} %s", [value]

        def _parse(dom):
            sql_parts = []
            values = []
            i = 0

            while i < len(dom):
                token = dom[i]

                if isinstance(token, tuple):
                    expr, val = to_sql(token)
                    sql_parts.append(expr)
                    values.extend(val)
                    i += 1

                elif isinstance(token, list):
                    sub_expr, sub_vals = _parse(token)
                    sql_parts.append(f"({sub_expr})")
                    values.extend(sub_vals)
                    i += 1

                elif token in ('and', 'or'):
                    sql_parts.append(token.upper())
                    i += 1

                else:
                    raise ValueError(f"Token inválido en dominio: {token}")

            return ' '.join(sql_parts), values

        return _parse(domain)

    @classmethod
    def search(cls, domain=None, order_by=None, limit=None):
        table_name = cls._meta.get('_name', cls.__name__.lower())
        where_clause = ""
        values = []

        if domain:
            where_clause, values = cls.parse_domain(domain)
            where_clause = f"WHERE {where_clause}"

        order_clause = f"ORDER BY {order_by}" if order_by else ""
        limit_clause = f"LIMIT {limit}" if limit else ""

        query = f"SELECT * FROM {table_name} {where_clause} {order_clause} {limit_clause};"

        conn = None
        try:
            conn = DatabasePool.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(query, values)
                return cursor.fetchall()
        finally:
            if conn:
                DatabasePool.release_connection(conn)