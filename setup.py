from setuptools import setup
import twitter_scraper.__version__

with open('README.md', 'r') as f:
   long_description = f.read()


setup(
   name='twitter-scraper',
   description='Twitter Scraper Python Package',
   version=twitter_scraper.__version__,
   long_description=long_description,
   long_description_content_type='text/markdown',
   url='https://github.com/milanXpetrovic/twitter_scraper',
   author='FIDIT - Fakultet informatike i digitalnih tehnologija',
   author_email='ured@inf.uniri.hr',
   maintainer='Andrea Hrelja',
   maintainer_email='andhrelja@hotmail.com',
   packages=[
      'twitter_scraper',
      'twitter_scraper.scrape',
      'twitter_scraper.clean',
      'twitter_scraper.graph',
      'twitter_scraper.text',
      'twitter_scraper.utils'
   ],
   classifiers=[
      'Development Status :: 5 - Production/Stable',
      'Environment :: Console',
      'Environment :: Other Environment',
      'Intended Audience :: Developers',
      'Intended Audience :: Education',
      'Intended Audience :: Information Technology',
      'Intended Audience :: System Administrators',
      'Operating System :: OS Independent',
      'Programming Language :: Python :: 3',
      'Programming Language :: Python :: 3 :: Only',
      'Programming Language :: Python :: 3.7',
      'Programming Language :: Python :: 3.8',
      'Programming Language :: Python :: 3.9',
      'Topic :: Scientific/Engineering :: Information Analysis',
      'Topic :: Software Development',
      'Topic :: Software Development :: Libraries',
      'Topic :: Software Development :: Libraries :: Python Modules'
   ],
   keywords=['twitter', 'scrape', 'data', 'big-data', 'data-analysis', 'data-engineering', 'topic-modeling', 'LDA'],
   package_dir={'twitter_scraper':'twitter_scraper'},
   install_requires=[
      'pandas==1.5.1',
      'tweepy==4.12.1',
      'stanza==1.4.2',
      'classla==1.2.0',
      'langid==1.1.6',
      'discord.py==2.0.1',
      'torch==1.12.0',
      'tqdm==4.62.3',
      'gensim==4.2.0'
   ],
   project_urls=dict(
      Documentation='https://github.com/milanXpetrovic/twitter_scraper/blob/master/docs/build/markdown/index.md',
      Source='https://github.com/milanXpetrovic/twitter_scraper',
      Issues='https://github.com/milanXpetrovic/twitter_scraper/issues',
      Changelog='https://github.com/milanXpetrovic/twitter_scraper/blob/master/CHANGELOG.md'
   )
)
