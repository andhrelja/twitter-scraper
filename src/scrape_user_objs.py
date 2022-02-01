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

OUTPUT_DIR = os.path.join(settings.OUTPUT_DIR, folder_name)
if not os.path.exists(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)

USER_INFO_CSV = os.path.join(OUTPUT_DIR, 'user-objs.csv')

def get_lookup_users(api, user_ids, retry_max=3, retry_delay=3):
    print("Collecting friends and follower objects...")
    
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
        finally:
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
        fileio.write_content(settings.USER_INFO_CSV, user_objs, 'csv')
        l.release()
        pbar.update(1)


if __name__ == '__main__':
    print("{} - Collecting user objects...".format(dt.datetime.now()))
    start_time = time.time()
    
    objs_size = 200
    collected_user_ids = utils.get_collected_user_ids()
    user_id_batches = utils.batches(collected_user_ids, objs_size)
    
    l = threading.Lock()
    q = queue.Queue()
    for user_ids in user_id_batches:
        q.put(user_ids)
    
    threads = []
    apis = utils.get_api_connections()
    pbar = tqdm(total=len(user_id_batches))
    for api in apis:
        thread = threading.Thread(target=collect_user_objs, args=(api,))
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()
    
    end_time = time.time()
    print("Time elapsed: {}s".format(end_time - start_time))
