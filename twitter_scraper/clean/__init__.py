"""
########
Cleaners
########

The :py:mod:twitter_scraper.clean module consists from three sub-modules.
The following modules clean the collected data output by :py:mod:twitter_scraper.scrape

1. :py:mod:twitter_scraper.clean.tweets
    * input: ``~/data/output/scrape/tweets/<user-id>.json``
    * output: ``~/data/output/clean/tweet/YYYY-MM-DD/tweets.csv``

2. :py:mod:twitter_scraper.clean.users
    * input: ``~/data/output/scrape/users/objs/user-objs.csv``
    * output: ``~/data/output/clean/user/YYY-MM-DD/users.csv``

"""

from .tweets import tweets
from .users import users