from setuptools import setup

setup(
   name='twitter-scraper',
   packages=[
      'twitter_scraper.scrape',
      'twitter_scraper.clean',
      'twitter_scraper.graph',
      'twitter_scraper.utils'
   ],
   # package_data='twitter_scraper/meta',
   package_dir={'twitter_scraper':'twitter_scraper'}
)