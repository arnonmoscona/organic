"""
This module exposes helper functions, mostly constructed around importlib, for dynamic importing,
loading, and reloading of modules and types
"""

import importlib.util

from free_range.core.common.exceptions import (InvalidArgumentError,
                                               NotFoundError)


def import_by_name(item_name, require_callable=False):
    module_name, var_name = _break_item_string(item_name)
    if (var_name is not None and var_name.strip() == ''
            or module_name is not None and module_name.strip() == ''):
                raise InvalidArgumentError(f'Invalid item name: "{var_name}"')

    try:
        spec = importlib.util.find_spec(module_name)
    except (AttributeError, ValueError) as ex:
        raise InvalidArgumentError(f'{module_name} could not be loaded.', caused_by=ex)

    if spec is None:
        raise NotFoundError(module_name, f'couldn\'t find module "{module_name}"')

    loaded_module = importlib.import_module(module_name)
    if not isinstance(loaded_module, type(importlib.util)):
        raise InvalidArgumentError(f'"{module_name}" does not reference a module. '
                                   f'Instead found {type(loaded_module)}')
    if var_name is None:
        if require_callable and not callable(loaded_module):
            raise InvalidArgumentError(f'The specified item name "{item_name}" is not callable')
        return loaded_module

    try:
        return_value = getattr(loaded_module, var_name)
        if require_callable and not callable(return_value):
            raise InvalidArgumentError(f'The specified item name "{item_name}" is not callable')
        return return_value
    except AttributeError as ex:
        raise NotFoundError(item_name, f'couldn\'nt find {var_name} in module {module_name}',
                            caused_by=ex)


def _break_item_string(name):
    if '.' not in name:
        return name, None
    parts = name.split('.')
    return '.'.join(parts[:-1]), parts[-1]
