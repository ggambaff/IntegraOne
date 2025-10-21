# -*- coding: utf-8 -*-
import sys

import integraone

from . import Command
from pathlib import Path


def run(args):
    config = integraone.tools.config.parse_config(args)

    preload = []
    if config['dbname']:
        preload = config['dbname'].split(',')
class Server(Command):
    """Start the odoo server (default command)"""
    def run(self, args):
        integraone.tools.config.parser.prog = f'{Path(sys.argv[0]).name} {self.name}'
        run(args)