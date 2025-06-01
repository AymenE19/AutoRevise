import logging


def setup_logger():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    return logging.getLogger(__name__)


def print_nested_dict(d, indent=0):
    """Recursively prints a nested dictionary with indentation."""
    for key, value in d.items():
        print('    ' * indent + str(key))
        if isinstance(value, dict):
            print_nested_dict(value, indent + 1)
        elif isinstance(value, list):
            for item in value:
                print('    ' * (indent + 1) + str(item))
        else:
            print('    ' * (indent + 1) + str(value))
