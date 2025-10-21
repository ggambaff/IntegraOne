# -*- coding: utf-8 -*-

import argparse
import json
import os


class configmanager(object):
    def __init__(self, fname=None):

        self.parser = parser = argparse.ArgumentParser(description="Arguments")

        group = parser.add_argument_group('Common options')
        group.add_argument("-c", "--config",dest="config",help="Specify alternate config file")

    def parse_config(self, args=None):
        parsed_args = self.parser.parse_args(args)

        config_path = parsed_args.config
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Archivo de configuración no encontrado: {config_path}")

        with open(config_path, 'r') as f:
            return json.load(f)

config = configmanager()