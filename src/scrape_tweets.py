import json
import os
import time
import queue
import threading
import datetime as dt
from tqdm import tqdm

import utils
import fileio
import settings

TWEET_MODEL = lambda x: {
    'id': x.get('id'),
    'user_id': x.get('user', {}).get('id'),
    'full_text': x.get('full_text'),
    'created_at': x.get('created_at')
}


def collect_users_tweets(conn_name, api):
    #Twitter only allows access to a users most recent 3240 tweets with this method
    #initialize a list to hold all the tweepy Tweets
    global q, l
    while not q.empty():
        pbar.update(1)
        user_id = q.get()

        all_user_tweets = []
        max_id = None
        new_tweets = [None]
        #keep grabbing tweets until there are no tweets left to grab
        while len(new_tweets) > 0:
            kwargs = dict(max_id=max_id, count=200, tweet_mode="extended")
            new_tweets, no_tweets = utils.get_twitter_endpoint(conn_name, api, 'user_timeline', user_id, retry_max=5, retry_delay=3, **kwargs)
            if new_tweets and new_tweets != [None] and not no_tweets:
                new_tweets = [TWEET_MODEL(item._json) for item in new_tweets]
                all_user_tweets.extend(new_tweets)
                oldest_tweet = new_tweets[-1]
                max_id = oldest_tweet['id']-1
                if dt.datetime.strptime(oldest_tweet['created_at'], '%a %b %d %H:%M:%S %z %Y').year <= 2020:
                    break
        
        if len(all_user_tweets) > 0:
            l.acquire()
            try:
                fileio.write_content(os.path.join(settings.USER_TWEETS_DIR, '{}.json'.format(user_id)), all_user_tweets, 'json')
                fileio.write_content(settings.PROCESSED_USER_TWEETS, user_id, 'json')
            except json.decoder.JSONDecodeError:
                print("\nJSONDecode error on {}.json".format(user_id))
            l.release()


if __name__ == '__main__':
    if not os.path.exists(settings.USER_TWEETS_DIR):
        os.mkdir(settings.USER_TWEETS_DIR)
    
    start_time = time.time()
    
    l = threading.Lock()
    q = queue.Queue()
    
    threads = []
    apis = utils.get_api_connections()
    
    baseline_user_ids = utils.get_baseline_user_ids(processed_filepath=settings.PROCESSED_USER_TWEETS)
    for user_id in baseline_user_ids:
        q.put(user_id)
    
    print("{} - Collecting tweets for baseline_user_ids...".format(dt.datetime.now()))
    pbar = tqdm(total=len(baseline_user_ids))
    for conn_name, api in apis.items():
        thread = threading.Thread(target=collect_users_tweets, args=(conn_name, api))
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()
    
    end_time = time.time()
    print("\n\nTime elapsed: {} min".format((end_time - start_time)/60))
