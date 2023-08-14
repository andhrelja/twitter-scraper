import sys
import json

if sys.version_info > (3, 9):
    import importlib.resources as pkg_resources
else:
    import importlib_resources as pkg_resources

version_path = pkg_resources.files(__package__) / 'version.json'
with open(version_path) as f:
    version_obj = json.load(f)
__version__ = version_obj['version']
print("twitter_scraper {}".format(__version__))
