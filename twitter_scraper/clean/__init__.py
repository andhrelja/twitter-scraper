"""
clean.users
===========

**Inputs**: 
    * ``~/data/output/scrape/users/objs/user-objs.csv``
    * ``~/data/input/locations.json``
**Outputs**: 
    * ``~/data/output/clean/user/YYYY-MM-DD/users.csv``

Artificial columns are created using the following rules:

* *is_croatian*: a User's location determined using naive text parsing and a static helper file (``locations.json``)
* *clean_location*: whitespace cleaned, user provided location or the value "Hrvatska"


Filter Users based on:

* *protected* = False
* *is_croatian* = True
* *statuses_count* > 10
* *friends_count* > 10
* *friends_count* < 5000
* *followers_count* > 10
* *followers_count* < 5000

Conforms User data to the following :mod:`pandas` schema:

.. code-block:: python

    USER_DTYPE = {
        'user_id':          'int64',
        'user_id_str':      'string',
        'name':             'string',
        'screen_name':      'string',
        'location':         'string',
        'description':      'string',
        'protected':        'boolean',
        'verified':         'boolean',
        'followers_count':  'int',
        'friends_count':    'int',
        'listed_count':     'int',
        'favourites_count': 'int',
        'statuses_count':   'int',
        'created_at':       'str',

        ### Custom columns
        'is_croatian':      'bool',
        'clean_location':   'string',
    }

**Example output:**

.. csv-table::
   :file: ../../docs/source/_static/clean_user.csv
   :widths: auto
   :header-rows: 1



clean.tweets
============

**Inputs**: 
    * ``~/data/output/scrape/tweets/<user-id>.json``
**Outputs**: 
    * ``~/data/output/clean/tweet/YYYY-MM-DD/tweets.csv``

Filter Tweets from 2021-08-01 onwards. Because this module is focused on working with ``csv`` formats, it transforms scraped ``json`` to clean ``csv``.
Conforms Tweet data to the following `pandas dtypes <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.dtypes.html>`_:

.. code-block:: python

    TWEET_DTYPE = {
        'id':               'string',
        'user_id':          'int64',
        'user_id_str':      'string',
        'full_text':        'string',
        'created_at':       'object',
        'hashtags':         'object',
        'user_mentions':    'object',
        'retweet_from_user_id':     'int64',
        'retweet_from_user_id_str': 'string',
        'geo':              'object',
        'coordinates':      'object',
        'retweet_count':    'int',
        'favorite_count':   'int',

        ### Custom columns
        'week': 'string',
        'month': 'string',
        'is_covid': 'bool'
    }

**Example output:**

.. csv-table::
   :file: ../../docs/source/_static/clean_tweet.csv
   :widths: auto
   :header-rows: 1

"""

from .users import update_filtered_baseline
from .tweets import tweets
from .tweets import TWEET_DTYPE
from .users import users
from .users import USER_DTYPE
