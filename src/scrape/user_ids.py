import os
import time
import threading
import queue
import datetime as dt
from tqdm import tqdm

import utils
import utils.fileio as fileio
from twitter_scraper import settings

baseline_user_ids = utils.get_baseline_user_ids(processed_filepath=settings.PROCESSED_USER_IDS)
pbar = tqdm(total=len(baseline_user_ids))

l = threading.Lock()
q = queue.Queue()

def collect_user_ids(conn_name, api):
    global q, l
    while not q.empty():
        pbar.update(1)
        user_id = q.get()

        friend_ids, missing_user = utils.get_twitter_endpoint(conn_name, api, 'get_friend_ids', user_id)
        if missing_user and not friend_ids:
            l.acquire()
            fileio.write_content(settings.MISSING_USER_IDS, int(missing_user), 'json')
            l.release()
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
        fileio.write_content(os.path.join(settings.USER_IDS_DIR, '{}.json'.format(user_id_str)), output_dict, 'json')
        fileio.write_content(settings.PROCESSED_USER_IDS, user_id, 'json')
        l.release()


def user_ids(apis):
    # 15 000 users in 28h
    global q, l
    
    if not os.path.exists(settings.USER_IDS_DIR):
        os.mkdir(settings.USER_IDS_DIR)
    
    start_time = time.time()
    
    threads = []
        
    for user_id in baseline_user_ids:
        q.put(user_id)
    
    print("{} - Scraping user ids ...".format(dt.datetime.now()))
    for conn_name, api in apis.items():
        thread = threading.Thread(target=collect_user_ids, args=(conn_name, api))
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()
    
    end_time = time.time()
    print("\n\nTime elapsed: {} min".format((end_time - start_time)/60))
