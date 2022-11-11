from .utils import fileio

version_obj = fileio.read_content('version.json', 'json')
__version__ = version_obj['version']
