# -*- coding: utf-8 -*-
import importlib
import os
import pkgutil
import sys
import logging

from integraone.modules.base import models
from integraone.config_loader import Config
from integraone.db import DatabasePool
from integraone.database_utils import ensure_database_exists, ensure_base_exists
from integraone.logging_config import setup_logging
from integraone.module_installer import install_modules
from integraone.web_server import start_web_server

_logger = logging.getLogger(__name__)


def parse_args():
    args = sys.argv[1:]
    config_path = None
    options = {}

    for arg in args:
        if arg.endswith(".json") and config_path is None:
            config_path = arg
        elif arg.startswith("--"):
            if "=" in arg:
                key, value = arg[2:].split("=", 1)
                options[key] = value
            else:
                options[arg[2:]] = True

    return config_path, options

def run():
    setup_logging()
    config_path, options = parse_args()

    if not config_path:
        print("Uso: python main.py <ruta_config.json> [--debug] [--env=dev]")
        sys.exit(1)

    _logger.info("Config path: %s", config_path)
    Config.load(config_path)
    _logger.info("Config: %s", Config.all())

    ensure_database_exists()
    base_created = ensure_base_exists()

    if options.get("debug"):
        print("Modo DEBUG activado")

    if "env" in options:
        print(f"Entorno seleccionado: {options['env']}")

    print("Inicializando pool de conexiones...")
    for loader, module_name, is_pkg in pkgutil.iter_modules(["C:\\Users\\gagf\\PycharmProjects\\IntegraOne\\integraone\\modules\\base\\models"]):
        importlib.import_module(f"{models.__name__}.{module_name}")
    DatabasePool.initialize()
    if not base_created:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        target_folder_path = os.path.join(script_dir, "modules")
        if not os.path.isdir(target_folder_path):
            print(f"Error: La ruta '{target_folder_path}' no existe o no es un directorio.")
            subfolders = []
        else:
            # 1. Usar os.listdir() para obtener todos los elementos (archivos y carpetas)
            all_items = os.listdir(target_folder_path)
            subfolders = [
                os.path.join(target_folder_path, item)
                for item in all_items
                # El filtro sigue verificando la ruta completa
                if os.path.isdir(os.path.join(target_folder_path, item))
            ]
            for folder in subfolders:
                install_modules(folder)

    print("Sistema listo.")

    # Iniciar servidor web
    start_web_server()