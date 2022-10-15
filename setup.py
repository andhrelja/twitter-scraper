from setuptools import setup
import json

with open('README.md', 'r') as f:
   long_description = f.read()

with open('requirements.txt', 'r') as f:
   install_requires = f.readlines()

with open('version.json', 'r') as f:
   version_obj = json.load(f)

setup(
   name='twitter-scraper',
   version=version_obj['version'],
   long_description=long_description,
   packages=[
      'twitter_scraper',
      'twitter_scraper.scrape',
      'twitter_scraper.clean',
      'twitter_scraper.graph',
      'twitter_scraper.text',
      'twitter_scraper.utils'
   ],
   package_dir={'twitter_scraper':'twitter_scraper'},
   install_requires=install_requires
)