from setuptools import setup

with open('requirements.txt', 'r') as f:
   install_requires = f.readlines()

setup(
   name='twitter-scraper',
   packages=[
      'twitter_scraper.scrape',
      'twitter_scraper.clean',
      'twitter_scraper.graph',
      'twitter_scraper.utils'
   ],
   package_dir={'twitter_scraper':'twitter_scraper'},
   install_requires=install_requires
)