from typing import List

import os
import queue
import threading
import tweepy
import datetime as dt
from tqdm import tqdm

from twitter_scraper import utils
from twitter_scraper.utils import fileio
from twitter_scraper import settings

logger = utils.get_logger(__file__)

l = threading.Lock()
q = queue.Queue()

MIN_DATE = dt.datetime.fromisoformat("2020-01-01T00:00:00+00:00")

def get_tweet_max_id(user_id: int):
    """Reads static ``input/max-tweet-ids`` JSON and returns the latest tweet ID. 
    Latest tweet ID value is used as ``since_id`` for incremental loads.

    :param user_id: User ID
    :type user_id: int
    :return: Latest tweet ID if exists, else None
    :rtype: Union[int, NoneType]
    """
    max_tweet_ids = fileio.read_content(os.path.join(settings.MAX_TWEET_IDS), 'json')
    if max_tweet_ids:
        return max_tweet_ids.get(user_id)
    return None

def __collect_users_tweets(conn_name: str, api: tweepy.API, pbar: tqdm):
    """Collects tweets for all user IDs read from ``baseline-user-ids.json`` using :mod:queue.
    This function is ran on multiple threads. The number of running threads matches the number of available Twitter API connections in :mod:twitter_scraper.settings.
    Retrieves all the user's tweets filtered by ``since_id`` and ``max_id``, applies the ``SCRAPE_TWEET`` transformation and appends the tweets to ``<user_id>.json``.

    :param conn_name: Twitter API connection name (:mod:twitter_scraper.settings)
    :type conn_name: str
    :param api: :py:class:tweepy.API object used to call Twitter API endpoints
    :type api: tweepy.API
    :param pbar: :mod:tqdm progress bar instance - total number of available user IDs, gets updated after a user's tweets are scraped
    :type pbar: tqdm.tqdm
    """
    # Twitter only allows access to 
    # a users most recent 3240 tweets with this method
    global q, l
    
    max_tweet_ids = {}
    while not q.empty():
        user_id = q.get()

        all_user_tweets = []
        since_id = get_tweet_max_id(user_id)
        max_id = None
        #keep grabbing tweets until there are no tweets left to grab
        while True:
            tweepy_kwargs = dict(since_id=since_id, max_id=max_id, count=200, tweet_mode="extended")
            new_tweets, _ = utils.get_twitter_endpoint(
                conn_name, api, 
                'user_timeline', 
                user_id, 
                retry_max=5, 
                retry_delay=3, 
                **tweepy_kwargs
            )
            
            if len(new_tweets) == 0:
                break
            else:
                oldest_tweet = new_tweets[-1]
                max_id = oldest_tweet.id - 1
                
                tweets = [item._json for item in new_tweets]
                all_user_tweets.extend(tweets)
                
                if oldest_tweet.created_at < MIN_DATE:
                    break
        
        max_tweet_ids[user_id] = max_id
        
        l.acquire()
        fileio.write_content(
            path=os.path.join(settings.SCRAPE_TWEETS_FN.format(user_id=user_id)), 
            content=all_user_tweets,
            file_type='json', 
            indent=None
        )
        l.release()
        pbar.update(1)
    if max_tweet_ids:
        fileio.write_content(settings.MAX_TWEET_IDS, max_tweet_ids, 'json', overwrite=True)


def tweets(apis: List[dict]):
    """
    1. Creates tweet scrape directory
    2. Enqueues user IDs from ``baseline-user-ids.json``
    3. Starts a :py:func:__collect_user_tweets thread for each connection in :mod:twitter_scraper.settings
    4. Waits until all threads complete executing

    :param apis: list of dictionaries: ``[{connection_name: tweepy.API}]``
    :type apis: List[dict]
    """
    global q, pbar
    
    start_time = dt.datetime.now(settings.TZ_INFO)
    utils.mkdir(settings.PROCESSED_SCRAPE_TWEETS_DIR)
    threads = []

    baseline_user_ids = utils.get_baseline_user_ids(processed_filepath=None)
    for user_id in baseline_user_ids:
        q.put(user_id)
    
    logger.info("Scraping Tweets")

    pbar = tqdm(total=len(baseline_user_ids), desc='scrape.tweets', position=-1)
    for conn_name, api in apis.items():
        thread = threading.Thread(
            target=__collect_users_tweets, 
            args=(conn_name, api, pbar)
        )
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()
    pbar.close()
    
    end_time = dt.datetime.now(settings.TZ_INFO)
    logger.info("Time elapsed: {} min".format(end_time - start_time))


if __name__ == '__main__':
    apis = utils.get_api_connections()
    tweets(apis)
