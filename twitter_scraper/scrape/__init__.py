"""
scrape.user_ids
===============

**Endpoints**: 
    * `followers/ids <https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-followers-ids>`_ 
    * `friends/ids <https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-friends-ids>`_ 
**Inputs**: 
    * ``~/data/input/baseline-user-ids.json``
**Outputs**: 
    * ``~/data/output/scrape/users/ids/<user-id>.json``


By collecting followers and friends data, this module retrieves source data to finally be used as graph **Edges**.

**Example outputs:**

.. code-block:: json

    {
        "<user-id>": {
            "friends_count": 8,
            "followers_count": 6,
            "friends": [
                848904702,
                219350809,
                536230802,
                3028905893,
                214826344,
                2801523007,
                1008662348,
                614676639
            ],
            "followers": [
                91446501,
                214826344,
                269747126,
                219350809,
                536230802,
                848904702
            ]
        }
    }

This data is later used to generate Graph edges by :mod:`twitter_scraper.graph.edges`.


scrape.user_objs
================

**Endpoints**: 
    * `users/lookup <https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-users-lookup>`_
**Inputs**: 
    * ``~/data/input/baseline-user-ids.json``
    * ``~/data/input/processed-user-objs.json``
**Outputs**: 
    * ``~/data/input/processed-user-objs.json``
    * ``~/data/output/scrape/users/objs/user-objs.csv``

The output will finally be used as graph **Nodes**.
Applies structural transformations to API response data. Original tweet JSON:

.. literalinclude:: _static/user.json
    :language: json

is transformed using the following mapping:

.. code-block:: python

    SCRAPE_USER = lambda x: {
        'user_id':          x.get('id'),
        'user_id_str':      x.get('id_str'),
        'name':             x.get('name'),
        'screen_name':      x.get('screen_name'),
        'location':         x.get('location'),
        "profile_location": x.get('profile_location'),
        'derived':          x.get('derived'),
        'url':              x.get('url'),
        'description':      x.get('description'),
        'protected':        x.get('protected'),
        'verified':         x.get('verified'),
        'followers_count':  x.get('followers_count'),
        'friends_count':    x.get('friends_count'),
        'listed_count':     x.get('listed_count'),
        'favourites_count': x.get('favourites_count'),
        'statuses_count':   x.get('statuses_count'),
        'created_at':       x.get('created_at'),
        'profile_banner_url':      x.get('profile_banner_url'),
        'profile_image_url_https': x.get('profile_image_url_https'),
        'default_profile':         x.get('default_profile'),
        'default_profile_image':   x.get('default_profile_image'),
        'withheld_in_countries':   x.get('withheld_in_countries'),
        'withheld_scope':          x.get('withheld_scope'),
    }

**Example output:**

.. csv-table::
   :file: ../../docs/source/_static/scrape_user.csv
   :widths: auto
   :header-rows: 1



scrape.tweets
=============

**Endpoints**: 
    * `statuses/user_timeline <https://developer.twitter.com/en/docs/twitter-api/v1/tweets/timelines/api-reference/get-statuses-user_timeline>`_
**Input**: 
    * ``~/data/input/baseline-user-ids.json``
    * ``~/data/output/scrape/users/ids/<user-id>.json`` (``max_id``)
**Output**: 
    * ``~/data/output/scrape/users/ids/<user-id>.json``

Applies structural transformations to API response data. Original tweet JSON:

.. literalinclude:: _static/tweet.json
    :language: json

is transformed using the following mapping:

.. code-block:: python

    SCRAPE_TWEET = lambda x, api=None: {
        'id':                   x.get('id'),
        'user_id':              x.get('user', {}).get('id'),
        'user_id_str':          x.get('user', {}).get('id_str'),
        'full_text':            x.get('full_text', x.get('text')),
        'created_at':           x.get('created_at'),
        'hashtags':             flatten_dictlist(x.get('entities', {}).get('hashtags', []), 'text'),
        'user_mentions':        flatten_dictlist(x.get('entities', {}).get('user_mentions', []), 'id'),
        'retweet_count':        x.get('retweet_count'),
        'retweeter_ids':        [],# api.get_retweeter_ids(x.get('id')),
        'retweet_from_user_id':         x.get('retweeted_status', {}).get('user', {}).get('id'),
        'retweet_from_user_id_str':     str(x.get('retweeted_status', {}).get('user', {}).get('id')),
        'in_reply_to_status_id':        x.get('in_reply_to_status_id'),
        'in_reply_to_status_id_str':    x.get('in_reply_to_status_id_str'),
        'in_reply_to_user_id':          x.get('in_reply_to_user_id'),
        'in_reply_to_user_id_str':      x.get('in_reply_to_user_id_str'),
        'in_reply_to_screen_name':      x.get('in_reply_to_screen_name'),
        'geo':                  x.get('geo'),
        'coordinates':          x.get('coordinates'),
        'place':                x.get('place'),
        'contributors':         x.get('contributors'),
        'is_quote_status':      x.get('is_quote_status'),
        'favorite_count':       x.get('favorite_count'),
        'favorited':            x.get('favorited'),
        'retweeted':            x.get('retweeted'),
        'possibly_sensitive':   x.get('possibly_sensitive'),
        'lang':                 x.get('lang')
    }

    flatten_dictlist = lambda dictlist, colname: [_dict.get(colname) for _dict in dictlist]

**Example outputs:**

.. literalinclude:: _static/scrape_tweet_1.json
    :language: json
    :caption: **146153494.json**

.. literalinclude:: _static/scrape_tweet_2.json
    :language: json
    :caption: **1488523272891375621.json**

"""

from .tweets import tweets
from .user_ids import user_ids
from .user_objs import user_objs