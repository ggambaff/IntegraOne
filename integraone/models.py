# -*- coding: utf-8 -*-
from integraone.fields import Field, IntegerField, CharField, DateTimeField, ManyToOne
from integraone.sql_executor import execute, fetch_all

class MetaModel(type):
    def __new__(cls, name, bases, attrs):
        fields = {}
        meta_attrs = {}
        default_fields = {
            'create_user': ManyToOne(to_model='system_users', description="Created by"),
            'write_user': ManyToOne(to_model='system_users', description="Last Updated by"),
            'create_date': DateTimeField(description="Created on"),
            'write_date': DateTimeField(description="Last Updated on")
        }
        fields['id'] = IntegerField(primary_key=True)
        for key, value in attrs.items():
            if isinstance(value, Field):
                fields[key] = value
            elif key.startswith('_'):
                meta_attrs[key] = value
        for key, field in default_fields.items():
            if key not in fields:
                fields[key] = field
        inherit_from = meta_attrs.get('_inherit')
        inherited_bases = []
        if isinstance(inherit_from, str):
            inherit_from = [inherit_from]
        if isinstance(inherit_from, list):
            for parent_name in inherit_from:
                parent = globals().get(parent_name)
                if parent and issubclass(parent, BaseModel):
                    inherited_bases.append(parent)
        bases = tuple(set(inherited_bases + list(bases)))
        attrs['_fields'] = fields
        attrs['_meta'] = meta_attrs
        return super().__new__(cls, name, bases, attrs)

class BaseModel(metaclass=MetaModel):
    _name = None
    _description = None

    def __init__(self, **kwargs):
        for field_name in self._fields:
            value = kwargs.get(field_name)
            setattr(self, field_name, value)
            setattr(self, f'_original_{field_name}', value)  # Guardar valor original

    @classmethod
    def _get_existing_columns(cls, table_name):
        query = """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = %s; \
                """
        result = fetch_all(query, [table_name])
        return [row[0] for row in result]  # Accede por índice si row es una tupla

    @classmethod
    def sync_table(cls):
        table_name = cls._meta.get('_model_name', cls.__name__.lower())
        model_fields = set(cls._fields.keys())
        db_fields = set(cls._get_existing_columns(table_name))

        to_add = model_fields - db_fields
        to_remove = db_fields - model_fields

        for field_name in to_add:
            field = cls._fields[field_name]
            alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {field_name} {field.sql()};"
            cls._execute(alter_sql)

        for field_name in to_remove:
            alter_sql = f"ALTER TABLE {table_name} DROP COLUMN {field_name};"
            cls._execute(alter_sql)

    @classmethod
    def create_table(cls):
        for name, field in cls._fields.items():
            if isinstance(field, ManyToOne):
                related_model = field.resolve_model()
                if related_model.__name__ != cls.__name__:
                    if hasattr(related_model, 'create_table'):
                        related_model.create_table()

        columns = []
        m2m_relations = []
        comments = []

        table_name = cls._meta.get('_model_name', cls.__name__.lower())
        reserved_keywords = {"user", "group", "order", "select", "system_user"}
        quoted_table = f'"{table_name}"' if table_name.lower() in reserved_keywords else table_name

        for name, field in cls._fields.items():
            if hasattr(field, 'field_type') and field.field_type:
                columns.append(f"{name} {field.sql()}")
                if hasattr(field, 'comment_sql'):
                    comment = field.comment_sql(quoted_table, name)
                    if comment:
                        comments.append(comment)
            elif hasattr(field, 'related_model') and hasattr(field, 'relation_table'):
                m2m_relations.append((name, field))

        query = f"CREATE TABLE IF NOT EXISTS {quoted_table} ({', '.join(columns)});"
        cls._execute(query)

        for name, field in m2m_relations:
            related_model = field.resolve_related_model()
            other_table = related_model._meta.get('_model_name', related_model.__name__.lower())
            quoted_other = f'"{other_table}"' if other_table.lower() in reserved_keywords else other_table
            rel_table = field.relation_table or f"{table_name}_{name}_rel"
            quoted_rel_table = f'"{rel_table}"' if rel_table.lower() in reserved_keywords else rel_table
            this_fk = f"{table_name}_id INTEGER REFERENCES {quoted_table}(id) ON DELETE CASCADE"
            other_fk = f"{quoted_other}_id INTEGER REFERENCES {quoted_other}(id) ON DELETE CASCADE"
            rel_query = f"CREATE TABLE IF NOT EXISTS {quoted_rel_table} ({this_fk}, {other_fk});"
            cls._execute(rel_query)

        # Sincronizar estructura de tabla con modelo
        cls.sync_table()

        for comment_sql in comments:
            cls._execute(comment_sql)

    def save(self):
        for field_name, field in self._fields.items():
            if field.options.get('logging'):
                old_value = getattr(self, f'_original_{field_name}', None)
                new_value = getattr(self, field_name, None)
                if old_value != new_value:
                    print(f"Campo '{field_name}' cambió de '{old_value}' a '{new_value}'")
        columns = ', '.join(self._fields.keys())
        values = ', '.join(['%s'] * len(self._fields))
        data = [getattr(self, key) for key in self._fields.keys()]
        table_name = self._meta.get('_model_name', self.__class__.__name__.lower())
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({values});"
        self._execute(query, data)

    @staticmethod
    def _execute(query, params=None):
        execute(query, params)

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
        table_name = cls._meta.get('_model_name', cls.__name__.lower())
        where_clause = ""
        values = []
        if domain:
            where_clause, values = cls.parse_domain(domain)
            where_clause = f"WHERE {where_clause}"
        order_clause = f"ORDER BY {order_by}" if order_by else ""
        limit_clause = f"LIMIT {limit}" if limit else ""
        query = f"SELECT * FROM {table_name} {where_clause} {order_clause} {limit_clause};"
        return fetch_all(query, values)