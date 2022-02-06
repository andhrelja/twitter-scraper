import os
import time
import queue
import threading
import datetime as dt
from tqdm import tqdm

import utils
import fileio
import settings


def collect_user_objs(conn_name, api):
    global q, l
    while not q.empty():
        pbar.update(1)
        user_ids = q.get()
        user_objs = utils.get_twitter_lookup_users(conn_name, api, user_ids)
        
        l.acquire()
        fileio.write_content(os.path.join(settings.USER_OBJS_DIR, 'user-objs.csv'), user_objs, 'csv')
        fileio.write_content(settings.PROCESSED_USER_OBJS, user_ids, 'json')
        l.release()


if __name__ == '__main__':
    if not os.path.exists(settings.USER_OBJS_DIR):
        os.mkdir(settings.USER_OBJS_DIR)
    
    start_time = time.time()
    
    l = threading.Lock()
    q = queue.Queue()
    
    threads = []
    apis = utils.get_api_connections()
    
    baseline_user_ids = utils.get_baseline_user_ids(
        processed_filepath=settings.PROCESSED_USER_OBJS, 
        users_friends_followers=True
    )
    user_id_batches = utils.batches(list(baseline_user_ids), 100)
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
