# -*- coding: utf-8 -*-
class MetaField(type):
    def __new__(cls, name, bases, attrs):
        print(f"Registrando clase de campo: {name}")
        return super().__new__(cls, name, bases, attrs)

class Field(metaclass=MetaField):
    def __init__(self, field_type, **kwargs):
        self.field_type = field_type
        self.options = kwargs

    def sql(self):
        sql_parts = [self.field_type]

        # NOT NULL
        if self.options.get('null') is False:
            sql_parts.append("NOT NULL")

        # DEFAULT
        if 'default' in self.options:
            default = self.options['default']
            if isinstance(default, str) and not default.upper().startswith("CURRENT_"):
                default = f"'{default}'"
            sql_parts.append(f"DEFAULT {default}")

        return ' '.join(sql_parts)

    def comment_sql(self, table_name, column_name):
        if 'description' in self.options:
            comment = self.options['description'].replace("'", "''")
            return f"COMMENT ON COLUMN {table_name}.{column_name} IS '{comment}';"
        return None

class CharField(Field):
    def __init__(self, **kwargs):
        super().__init__("varchar", **kwargs)

class IntegerField(Field):
    def __init__(self, primary_key=False, **kwargs):
        field_type = "SERIAL" if primary_key else "INTEGER"
        super().__init__(field_type, **kwargs)

class BooleanField(Field):
    def __init__(self, default=False, **kwargs):
        super().__init__("BOOLEAN", default=default, **kwargs)

class FloatField(Field):
    def __init__(self, **kwargs):
        super().__init__("REAL", **kwargs)

class DateField(Field):
    def __init__(self, **kwargs):
        super().__init__("DATE", **kwargs)

class DateTimeField(Field):
    def __init__(self, **kwargs):
        super().__init__("TIMESTAMP", **kwargs)

class TextField(Field):
    def __init__(self, **kwargs):
        super().__init__("TEXT", **kwargs)


class ManyToOne(Field):  # Many2One
    def __init__(self, to_model, on_delete='CASCADE', **kwargs):
        self.to_model = to_model  # Puede ser string o clase
        self.on_delete = on_delete
        self._resolved_model = None
        super().__init__(field_type=None, **kwargs)

    def resolve_model(self):
        if self._resolved_model:
            return self._resolved_model

        if isinstance(self.to_model, str):
            try:
                from integraone import models
                BaseModel = getattr(models, 'BaseModel', None)
                if BaseModel:
                    for subclass in BaseModel.__subclasses__():
                        if getattr(subclass, '_model_name', '').lower() == self.to_model.lower():
                            self._resolved_model = subclass
                            break
            except ImportError as e:
                print(e)
        else:
            self._resolved_model = self.to_model

        return self._resolved_model

    def sql(self):
        model = self.resolve_model()
        if model:
            table = model._meta.get('_model_name', model.__name__.lower())
            return f"INTEGER REFERENCES {table}(id) ON DELETE {self.on_delete}"
        return "INTEGER"


class OneToMany(Field):
    def __init__(self, related_model, related_field, **kwargs):
        self.related_model = related_model  # Puede ser string o clase
        self.related_field = related_field
        self._resolved_model = None
        super().__init__(field_type=None, **kwargs)

    def resolve_related_model(self):
        if isinstance(self.related_model, str):
            from models import BaseModel
            for subclass in BaseModel.__subclasses__():
                if getattr(subclass, '_model_name', '').lower() == self.related_model.lower():
                    self._resolved_model = subclass
                    break
        else:
            self._resolved_model = self.related_model
        return self._resolved_model


class ManTo2Many(Field):
    def __init__(self, related_model, relation_table=None, **kwargs):
        self.related_model = related_model  # Puede ser string o clase
        self.relation_table = relation_table
        self._resolved_model = None
        super().__init__(field_type=None, **kwargs)

    def resolve_related_model(self):
        if isinstance(self.related_model, str):
            from models import BaseModel
            for subclass in BaseModel.__subclasses__():
                if getattr(subclass, '_model_name', '').lower() == self.related_model.lower():
                    self._resolved_model = subclass
                    break
        else:
            self._resolved_model = self.related_model
        return self._resolved_model