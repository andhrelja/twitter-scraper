import os
import time
import json
import tweepy
import queue
import threading
import datetime as dt
import requests.exceptions
from tqdm import tqdm

import utils
import fileio
import settings

now = dt.datetime.now()
folder_name = now.strftime('%Y-%m-%d')

OUTPUT_DIR = os.path.join(settings.OUTPUT_DIR, folder_name)
if not os.path.exists(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)

USER_OBJS_CSV = os.path.join(OUTPUT_DIR, 'user-objs.csv')


def get_twitter_lookup_users(conn_name, api, user_ids, retry_max=3, retry_delay=3):
    retry_num = 0
    while retry_num < retry_max:
        try:
            batch_users = api.lookup_users(user_id=user_ids)
        except tweepy.errors.TwitterServerError: # 503
            print("\nTwitterServerError: try #{}, {}s delay".format(retry_num+1, retry_delay))
            time.sleep(retry_delay)
            retry_num += 1
        except tweepy.errors.TweepyException:
            api = utils.reconnect_api(conn_name)
            print("\nTweepyException: try #{}, {}s delay".format(retry_num+1, retry_delay))
            time.sleep(retry_delay)
            retry_num += 1
        except requests.exceptions.ConnectionError:
            api = utils.reconnect_api(conn_name)
            print("\nConnectionError: try #{}, {}s delay".format(retry_num+1, retry_delay))
            time.sleep(retry_delay)
            retry_num += 1
        else:
            _content = [user._json for user in batch_users]
            content = [
                {
                    'user_id': user.get('id'), 
                    'location': user.get('location'),
                    'screen_name': user.get('screen_name'), 
                    'name': user.get('name'), 
                    'statuses_count': user.get('statuses_count'), 
                    'friends_count': user.get('friends_count'), 
                    'followers_count': user.get('followers_count'),
                    'description': user.get('description'),
                    'created_at': user.get('created_at'), 
                    'verified': user.get('verified'),
                    'protected': user.get('protected')
                } for user in _content
            ]
            return content


def collect_user_objs(conn_name, api):
    global q, l
    while not q.empty():
        user_ids = q.get()
        user_objs = get_twitter_lookup_users(conn_name, api, user_ids)
        l.acquire()
        fileio.write_content(USER_OBJS_CSV, user_objs, 'csv')
        l.release()
        pbar.update(1)


def get_collected_user_ids():
    latest_scrape_date = max(filter(None, [item if os.path.isdir(os.path.join(settings.INPUT_DIR, item)) else None for item in os.listdir(settings.INPUT_DIR)]))
    
    print("Getting collected user ids for {}...".format(latest_scrape_date))
    content = {}
    for file_name in tqdm(os.listdir(os.path.join(settings.INPUT_DIR, latest_scrape_date))):
        file_path = os.path.join(settings.INPUT_DIR, latest_scrape_date, file_name)
        with open(file_path, 'r') as f:
            content.update(json.load(f))
    
    print("Appending friends and followers to user_id list...")
    all_user_ids = set(fileio.read_content(settings.MISSING_USER_IDS, 'json'))
    for user_id, user_info in tqdm(list(content.items())):
        all_user_ids.add(user_id)
        all_user_ids = all_user_ids.union(user_info.get('friends'))
        all_user_ids = all_user_ids.union(user_info.get('followers'))
    
    collected_user_obj_ids = fileio.read_content(USER_OBJS_CSV, 'csv', column='user_id')
    all_user_ids.difference_update(map(int, collected_user_obj_ids))
    return all_user_ids


if __name__ == '__main__':
    start_time = time.time()
    
    l = threading.Lock()
    q = queue.Queue()
    
    threads = []
    apis = utils.get_api_connections()
    
    collected_user_ids = get_collected_user_ids()
    user_id_batches = utils.batches(list(collected_user_ids), 100)
    for user_ids in user_id_batches:
        q.put(user_ids)
    
    print("{} - Collecting user objects...".format(dt.datetime.now()))
    pbar = tqdm(total=len(user_id_batches))
    for conn_name, api in apis.items():
        thread = threading.Thread(target=collect_user_objs, args=(conn_name, api))
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()
    
    end_time = time.time()
    print("\n\nTime elapsed: {} min".format((end_time - start_time)/60))
