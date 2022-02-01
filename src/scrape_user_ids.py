import os
import time
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

INPUT_DIR = os.path.join(settings.INPUT_DIR, folder_name)
if not os.path.exists(INPUT_DIR):
    os.mkdir(INPUT_DIR)


def get_paginated_twitter_content(api, api_method_name, user_id, retry_max=3, retry_delay=3):
    content = []
    
    conn_name, api = list(api.items())[0]
    method = getattr(api, api_method_name)
    cursor = tweepy.Cursor(method=method, user_id=user_id)

    retry_num = 0
    while retry_num < retry_max:
        try:
            for page in cursor.pages():
                content.extend(page)
            return content, None
        except tweepy.errors.NotFound: # 404
            return content, user_id
        except tweepy.errors.Unauthorized: # 401
            return content, user_id
        except requests.exceptions.ConnectionError:
            api = utils.reconnect_api(conn_name)
            method = getattr(api, api_method_name)
            cursor = tweepy.Cursor(method=method, user_id=user_id)
            print("\nConnectionError: try #{}, {}s delay".format(retry_num+1, retry_delay))
            time.sleep(retry_delay)
            retry_num += 1
    
    return content, None


def collect_user_ids(api):
    global q, l
    while not q.empty():
        pbar.update(1)
        user_id = q.get()
        output_dict = {}
        
        friend_ids, inactive_user = get_paginated_twitter_content(api, 'get_friend_ids', user_id)
        if inactive_user and not friend_ids:
            l.acquire()
            fileio.write_content(settings.MISSING_USER_IDS, [int(inactive_user)], 'json')
            l.release()
            continue
        
        follower_ids, _ = get_paginated_twitter_content(api, 'get_follower_ids', user_id)
        
        user_id_str = str(user_id)
        output_dict[user_id_str] = {
            'friends_count': len(friend_ids),
            'followers_count': len(follower_ids),
            'friends': friend_ids,
            'followers': follower_ids
        }
        l.acquire()
        fileio.write_content(os.path.join(INPUT_DIR, '{}.json'.format(user_id_str)), output_dict, 'json')
        fileio.write_content(settings.PROCESSED_USER_IDS, [user_id], 'json')
        l.release()
        


def get_initial_user_ids():
    baseline_user_ids = fileio.read_content(settings.BASELINE_USER_IDS, 'json')
    missing_user_ids = fileio.read_content(settings.MISSING_USER_IDS, 'json')
    processed_user_ids = fileio.read_content(settings.PROCESSED_USER_IDS, 'json')
    
    initial_user_ids = set(baseline_user_ids)
    initial_user_ids.difference_update(missing_user_ids)
    initial_user_ids.difference_update(processed_user_ids)
    return initial_user_ids


if __name__ == '__main__':
    start_time = time.time()
    
    initial_user_ids = get_initial_user_ids()
    
    l = threading.Lock()
    q = queue.Queue()
    for user_id in initial_user_ids:
        q.put(user_id)
    
    threads = []
    apis = utils.get_api_connections()
    
    print("{} - Collecting friends and follower IDs for initial_user_ids...".format(dt.datetime.now()))
    pbar = tqdm(total=len(initial_user_ids))
    for api in apis:
        thread = threading.Thread(target=collect_user_ids, args=(api,))
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()
    
    end_time = time.time()
    print("\n\nTime elapsed: {} min".format((end_time - start_time)/60))
