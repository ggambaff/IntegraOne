# -*- coding: utf-8 -*-
import sys



commands = {}
class Command:
    name = None
    def __init_subclass__(cls):
        cls.name = cls.name or cls.__name__.lower()
        commands[cls.name] = cls

def run():
    args = sys.argv[1:]