# -*- coding: utf-8 -*-
import os
import importlib.util
import inspect
import sys
import logging
from pathlib import Path
from typing import Union
import yaml
from integraone import models

_logger = logging.getLogger(__name__)

def install_modules(modules_root: Union[str, os.PathLike]):
    """
    Recorre una carpeta raíz que contiene múltiples subpaquetes y subcarpetas internas,
    importa dinámicamente los modelos desde cualquier subcarpeta y ejecuta create_table()
    en las clases que lo tengan.
    """
    if not os.path.isdir(modules_root):
        _logger.error(f"The path '{modules_root}' is not a valid directory.")
        return

    sys.path.insert(0, str(modules_root))
    package_yaml_file = None
    signal_file = None
    for root, dirs, files in os.walk(modules_root):
        for file_name in files:
            full_file_path = os.path.join(root, file_name)
            if file_name == 'package.yaml':
                package_yaml_file = full_file_path
            if file_name == 'signals.py':
                signal_file = full_file_path

    try:
        # 2. Abre y lee el archivo
        with open(package_yaml_file, 'r') as f:
            # 3. Usa safe_load() para parsear el YAML a un objeto de Python (diccionario/lista)
            datos_configuracion = yaml.safe_load(f)

        # 4. Los datos ya están cargados y puedes acceder a ellos como un diccionario
        BaseModel = getattr(models, 'BaseModel', None)
        models_ids = BaseModel.__subclasses__()
        for model in datos_configuracion.get('models'):
            model_id = next(filter(lambda x: x._model_name== model,models_ids),None)
            if model_id is not None:
                model_id.create_table()
        post_installS = datos_configuracion.get('post_install')
        if post_installS is not None:
            file_path = Path(signal_file)
            module_name = file_path.stem
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None:
                raise FileNotFoundError(f"No se pudo encontrar el archivo del módulo en la ruta: {signal_file}")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            for post_install in post_installS:
                if not hasattr(module, method_name_str):
                    raise AttributeError(f"El módulo '{module_name}' no tiene el método '{method_name_str}'.")


    except FileNotFoundError:
        print(f"❌ Error: El archivo '{package_yaml_file}' no se encontró.")
    except yaml.YAMLError as exc:
        print(f"❌ Error al parsear el archivo YAML: {exc}")
    except Exception as e:
        print(f"❌ Ocurrió un error inesperado: {e}")


    # for root, dirs, files in os.walk(modules_root):
    #     for filename in files:
    #         if filename.endswith('.py') and not filename.startswith('__'):
    #             module_name = filename[:-3]
    #             file_path = os.path.join(root, filename)
    #
    #             # Generar un nombre único para el módulo basado en su ruta
    #             module_id = os.path.relpath(file_path, modules_root).replace(os.sep, '_').replace('.py', '')
    #
    #             spec = importlib.util.spec_from_file_location(module_id, file_path)
    #             if spec and spec.loader:
    #                 try:
    #                     module = importlib.util.module_from_spec(spec)
    #                     sys.modules[module_id] = module
    #                     spec.loader.exec_module(module)
    #                     ff = inspect.getmembers(module, inspect.isclass)
    #                     BaseModel = getattr(models, 'BaseModel', None)
    #                     ggg = BaseModel.__subclasses__()
    #
    #                     for name, obj in inspect.getmembers(module, inspect.isclass):
    #                         if hasattr(obj, 'create_table') and callable(getattr(obj, 'create_table')):
    #                             _logger.debug(f"Creating table for model: {name}")
    #                             obj.create_table()
    #                 except Exception as e:
    #                     print(f"Error processing module {module_name}: {e}")