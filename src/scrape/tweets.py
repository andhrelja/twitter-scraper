import os
import time
import queue
import threading
import datetime as dt
from tqdm import tqdm

import utils
import utils.fileio as fileio
from twitter_scraper import settings

logger = utils.get_logger(__file__)

l = threading.Lock()
q = queue.Queue()

baseline_user_ids = utils.get_baseline_user_ids(processed_filepath=settings.PROCESSED_USER_TWEETS)

flatten_dictlist = lambda dictlist, colname: [_dict.get(colname) for _dict in dictlist]
SCRAPE_TWEET = lambda x: {
    'id':               x.get('id'),
    'user_id':          x.get('user', {}).get('id'),
    'full_text':        x.get('full_text', x.get('text')),
    'created_at':       x.get('created_at'),
    'hashtags':         flatten_dictlist(x.get('entities', {}).get('hashtags', []), 'text'),
    'user_mentions':    flatten_dictlist(x.get('entities', {}).get('user_mentions', []), 'id'),
    'retweet_user':     x.get('retweeted_status', {}).get('user', {}).get('id'),
    'retweet_count':    x.get('retweet_count'),
	'in_reply_to_status_id':      x.get('in_reply_to_status_id'),
	'in_reply_to_status_id_str':  x.get('in_reply_to_status_id_str'),
	'in_reply_to_user_id':        x.get('in_reply_to_user_id'),
	'in_reply_to_user_id_str':    x.get('in_reply_to_user_id_str'),
	'in_reply_to_screen_name':    x.get('in_reply_to_screen_name'),
	'geo':              x.get('geo'),
	'coordinates':      x.get('coordinates'),
	'place':            x.get('place'),
	'contributors':     x.get('contributors'),
	'is_quote_status':  x.get('is_quote_status'),
	'favorite_count':   x.get('favorite_count'),
	'favorited':        x.get('favorited'),
	'retweeted':        x.get('retweeted'),
	'possibly_sensitive': x.get('possibly_sensitive'),
	'lang':             x.get('lang')
}


def get_tweet_max_id(user_id):
    user_tweets = fileio.read_content(os.path.join(settings.USER_TWEETS_DIR, '{}.json'.format(user_id)), 'json')
    if user_tweets:
        latest_tweet = max(user_tweets, key=lambda x: x['id'])
        return latest_tweet['id']
    return None


def collect_users_tweets(conn_name, api, pbar):
    # Twitter only allows access to 
    # a users most recent 3240 tweets with this method
    global q, l
    
    while not q.empty():
        pbar.update(1)
        user_id = q.get()

        all_user_tweets = []
        max_id = get_tweet_max_id(user_id)
        #keep grabbing tweets until there are no tweets left to grab
        while True:
            tweepy_kwargs = dict(max_id=max_id, count=200, tweet_mode="extended")
            new_tweets, no_tweets = utils.get_twitter_endpoint(conn_name, api, 'user_timeline', user_id, retry_max=5, retry_delay=3, **tweepy_kwargs)
            if new_tweets and not no_tweets:
                new_tweets = [SCRAPE_TWEET(item._json) for item in new_tweets]
                #new_tweets = [item._json for item in new_tweets]
                all_user_tweets.extend(new_tweets)
                oldest_tweet = new_tweets[-1]
                max_id = oldest_tweet['id']-1
                if dt.datetime.strptime(oldest_tweet['created_at'], '%a %b %d %H:%M:%S %z %Y').year <= 2020:
                    break
            else:
                break
        
        l.acquire()
        fileio.write_content(
            os.path.join(settings.USER_TWEETS_DIR, '{}.json'.format(user_id)), 
            all_user_tweets, 'json'
        )
        fileio.write_content(settings.PROCESSED_USER_TWEETS, user_id, 'json')
        l.release()


def tweets(apis):
    global q, baseline_user_ids, pbar
    start_time = time.time()
    utils.mkdir(settings.USER_TWEETS_DIR)

    # if settings.DEBUG:
    #     limit = 10
    #     baseline_user_ids = list(baseline_user_ids)[:limit]
    
    threads = []
    for user_id in baseline_user_ids:
        q.put(user_id)
    
    logger.info("Scraping Tweets")
    pbar = tqdm(total=len(baseline_user_ids))
    
    for conn_name, api in apis.items():
        thread = threading.Thread(
            target=collect_users_tweets, 
            args=(conn_name, api, pbar)
        )
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()
    
    pbar.close()
    end_time = time.time()
    logger.info("Time elapsed: {} min".format((end_time - start_time)/60))


if __name__ == '__main__':
    apis = utils.get_api_connections()
    tweets(apis)