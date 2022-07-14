"""
User IDs Scraper
-------

Uses `followers/ids <https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-followers-ids>`_ 
and `friends/ids <https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-friends-ids>`_ 
to collect follower and friend IDs for a given User ID.

This data is later used to generate Graph edges by :mod:twitter_scraper.graph.edges.

By collecting followers and friends data, this module creates a graph node similar to the following:

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


Input
------

``~/data/input/baseline-user-ids.json``

Output
------

``~/data/output/scrape/users/ids/<user-id>.json``

"""
import os
import time
import queue
import threading
from tqdm import tqdm

from twitter_scraper import utils
from twitter_scraper.utils import fileio
from twitter_scraper import settings

logger = utils.get_logger(__file__)

l = threading.Lock()
q = queue.Queue()

baseline_user_ids = utils.get_baseline_user_ids(processed_filepath=settings.PROCESSED_USER_IDS)


def __collect_user_ids(conn_name, api, pbar):
    global q, l
    
    while not q.empty():
        user_id = q.get()

        friend_ids, missing_user = utils.get_twitter_endpoint(conn_name, api, 'get_friend_ids', user_id)
        if missing_user and not friend_ids:
            l.acquire()
            fileio.write_content(settings.MISSING_USER_IDS, int(missing_user), 'json')
            l.release()
            pbar.update(1)
            continue
        follower_ids, _ = utils.get_twitter_endpoint(conn_name, api, 'get_follower_ids', user_id)
        
        user_id_str = str(user_id)
        output_dict = {
            user_id_str: {
                'friends_count': len(friend_ids),
                'followers_count': len(follower_ids),
                'friends': friend_ids,
                'followers': follower_ids
            }
        }
        
        l.acquire()
        fileio.write_content(os.path.join(settings.USER_IDS_DIR, '{}.json'.format(user_id_str)), output_dict, 'json', overwrite=True)
        # fileio.write_content(settings.PROCESSED_USER_IDS, user_id, 'json')
        l.release()
        pbar.update(1)


def user_ids(apis):
    # 15 requests per connection
    # 15 min wait until new requests are available
    # 15*9=135 users per connection
    # 135 users / 3 sec
    # 15 000 users in 28h
    # 35 000 users in 65h
    
    global q, baseline_user_ids

    start_time = time.time()
    threads = []
    
    utils.mkdir(settings.USER_IDS_DIR)
    
    for user_id in baseline_user_ids:
        q.put(user_id)
    
    logger.info("Scraping User IDs")

    pbar = tqdm(total=len(baseline_user_ids))
    for conn_name, api in apis.items():
        thread = threading.Thread(
            target=__collect_user_ids, 
            args=(conn_name, api, pbar)
        )
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()
    pbar.close()

    end_time = time.time()
    logger.info("Time elapsed: {} min".format(round((end_time - start_time)/60, 2)))


if __name__ == '__main__':
    apis = utils.get_api_connections()
    user_ids(apis)