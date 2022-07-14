"""
########
Scrapers
########

The :py:mod:twitter_scraper.scrape module consists from three sub-modules.
The following modules collect data using their respected Twitter endpoints:

1. :py:mod:twitter_scraper.scrape.tweets
    * `statuses/user_timeline <https://developer.twitter.com/en/docs/twitter-api/v1/tweets/timelines/api-reference/get-statuses-user_timeline>`_
        * loads history using Tweet IDs: ``since_id=None, max_id=None``
        * loads incremental using Tweet IDs: ``since_id=max_latest_id, max_id=None``
        * limit: 
            * 900 requests / 15 mins (using 9 threads = **8100 requests / 15 mins**)
            * 3200 of a user's most recent Tweets
        * output: ``~/data/output/scrape/tweets/<user-id>.json``

2. :py:mod:twitter_scraper.scrape.user_ids
    * `followers/ids <https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-followers-ids>`_
        * loads all follower ids for every baseline User ID (~/data/input/baseline-user-ids.json``)
        * limit: 15 requests / 15 mins (using 9 threads = **135 requests / 15 mins**)
        * output: ``~/data/output/scrape/users/ids/<user-id>.json``

    * `friends/ids <https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-friends-ids>`_
        * loads all friend ids for every baseline User ID (~/data/input/baseline-user-ids.json``)
        * limit: 15 requests / 15 mins (using 9 threads = **135 requests / 15 mins**)
        * finds missing User IDs (~/data/input/missing-user-ids.json``)
        * output: ``~/data/output/scrape/users/ids/<user-id>.csv``

3. :py:mod:twitter_scraper.scrape.user_obj
    * `users/show <https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-users-show>`_
        * loads all user objects for every baseline User ID (~/data/input/baseline-user-ids.json``)
        * limit: 15 requests / 15 mins (using 9 threads = **135 requests / 15 mins**)
        * filter missing User IDs (~/data/input/missing-user-ids.json``)
        * filter processed User IDs (~/data/input/processed-user-ids.json``)
        * output: 
            * ``~/data/input/processed-user-ids.json``
            * ``~/data/output/scrape/users/objs/user-objs.csv``

"""
from .tweets import tweets
from .user_ids import user_ids
from .user_objs import user_objs