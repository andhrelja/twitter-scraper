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


def get_lookup_users(api, user_ids, retry_max=3, retry_delay=3):
    conn_name, api = list(api.items())[0]
    retry_num = 0
    while retry_num < retry_max:
        try:
            batch_users = api.lookup_users(user_id=user_ids)
        except tweepy.errors.TwitterServerError: # 503
            print("\nTwitterServerError: trying again for {} times, {}s delay".format(retry_num, retry_delay))
            time.sleep(retry_delay)
            retry_num += 1
        except requests.exceptions.ConnectionError:
            api = utils.reconnect_api(conn_name)
            print("\nConnectionError: trying again for {} times, {}s delay".format(retry_num, retry_delay))
            time.sleep(retry_delay)
            retry_num += 1
        else:
            _content = [user._json for user in batch_users]
            content = [
                {
                    'user_id': user.get('id'), 
                    'screen_name': user.get('screen_name'), 
                    'created_at': user.get('created_at'), 
                    'verified': user.get('verified'), 
                    'url': user.get('url'), 
                    'name': user.get('name'), 
                    'description': user.get('description'),
                    'statuses_count': user.get('statuses_count'), 
                    'friends_count': user.get('friends_count'), 
                    'followers_count': user.get('followers_count'), 
                    'location': user.get('location')
                } for user in _content
            ]
            return content


def collect_user_objs(api):
    global q, l
    while not q.empty():
        user_ids = q.get()
        user_objs = get_lookup_users(api, user_ids)
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
    all_user_ids = set()
    for user_id, user_info in tqdm(content.items()):
        all_user_ids.add(user_id)
        all_user_ids = all_user_ids.union(user_info.get('friends'))
        all_user_ids = all_user_ids.union(user_info.get('followers'))
    
    collected_user_obj_ids = fileio.read_content(USER_OBJS_CSV, 'csv', column='user_id')
    all_user_ids.difference_update(map(int, collected_user_obj_ids))
    return all_user_ids


if __name__ == '__main__':
    start_time = time.time()
    
    collected_user_ids = get_collected_user_ids()
    user_id_batches = utils.batches(list(collected_user_ids), 100)
    
    l = threading.Lock()
    q = queue.Queue()
    for user_ids in user_id_batches:
        q.put(user_ids)
    
    threads = []
    apis = utils.get_api_connections()
    
    print("{} - Collecting user objects...".format(dt.datetime.now()))
    pbar = tqdm(total=len(user_id_batches))
    for api in apis:
        thread = threading.Thread(target=collect_user_objs, args=(api,))
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()
    
    end_time = time.time()
    print("Time elapsed: {} min".format((end_time - start_time)/60))
