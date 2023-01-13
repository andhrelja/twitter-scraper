import importlib_resources
import json

version_path = importlib_resources.files(__package__) / 'version.json'
with open(version_path) as f:
    version_obj = json.load(f)
__version__ = version_obj['version']
