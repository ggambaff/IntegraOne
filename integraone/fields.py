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
        return self.field_type

class CharField(Field):
    def __init__(self, max_length=255):
        super().__init__(f"VARCHAR({max_length})")

class IntegerField(Field):
    def __init__(self, primary_key=False):
        field_type = "SERIAL" if primary_key else "INTEGER"
        super().__init__(field_type)

class ForeignKey(Field):
    def __init__(self, to_model, on_delete='CASCADE'):
        self.to_model = to_model
        self.on_delete = on_delete
        super().__init__(f"INTEGER REFERENCES {to_model.__name__.lower()}(id) ON DELETE {on_delete}")