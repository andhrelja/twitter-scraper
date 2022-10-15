from setuptools import setup

with open('requirements.txt', 'r') as f:
   install_requires = f.readlines()

setup(
   name='twitter-scraper',
   version='0.0.2',
   packages=[
      'twitter_scraper.scrape',
      'twitter_scraper.clean',
      'twitter_scraper.graph',
      'twitter_scraper.text',
      'twitter_scraper.utils',
      'twitter_scraper'
   ],
   package_dir={'twitter_scraper':'twitter_scraper'},
   install_requires=install_requires
)