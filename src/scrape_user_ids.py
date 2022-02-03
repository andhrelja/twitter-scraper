import os
import time
import queue
import threading
import datetime as dt
from tqdm import tqdm

import utils
import fileio
import settings

now = dt.datetime.now()
folder_name = now.strftime('%Y-%m-%d')
#folder_name = '2022-02-01'

INPUT_DIR = os.path.join(settings.INPUT_DIR, folder_name)
if not os.path.exists(INPUT_DIR):
    os.mkdir(INPUT_DIR)


def collect_user_ids(conn_name, api):
    global q, l
    while not q.empty():
        pbar.update(1)
        user_id = q.get()

        friend_ids, inactive_user = utils.get_twitter_endpoint(conn_name, api, 'get_friend_ids', user_id)
        if inactive_user and not friend_ids:
            l.acquire()
            fileio.write_content(settings.MISSING_USER_IDS, int(inactive_user), 'json')
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
        fileio.write_content(os.path.join(INPUT_DIR, '{}.json'.format(user_id_str)), output_dict, 'json')
        fileio.write_content(settings.PROCESSED_USER_IDS, user_id, 'json')
        l.release()


def get_output_user_ids(input_folder_name):
    output_user_ids = set()
    for file_name in os.listdir(os.path.join(settings.INPUT_DIR, input_folder_name)):
        user_id = file_name.replace('.json', '')
        output_user_ids.add(int(user_id))
    return output_user_ids


def get_initial_user_ids(input_folder_name=None):
    initial_user_ids = set(fileio.read_content(settings.BASELINE_USER_IDS, 'json'))
    missing_user_ids = set(fileio.read_content(settings.MISSING_USER_IDS, 'json'))
    processed_user_ids = set(fileio.read_content(settings.PROCESSED_USER_IDS, 'json'))
    
    if input_folder_name:
        output_user_ids = get_output_user_ids(input_folder_name)
        initial_user_ids.difference_update(output_user_ids)
        
    initial_user_ids.difference_update(missing_user_ids)
    initial_user_ids.difference_update(processed_user_ids)
    return initial_user_ids


if __name__ == '__main__':
    start_time = time.time()
    
    l = threading.Lock()
    q = queue.Queue()
    
    threads = []
    apis = utils.get_api_connections()
    
    initial_user_ids = get_initial_user_ids(input_folder_name='2022-02-01')
    for user_id in initial_user_ids:
        q.put(user_id)
    
    print("{} - Collecting friends and follower IDs for initial_user_ids...".format(dt.datetime.now()))
    pbar = tqdm(total=len(initial_user_ids))
    for conn_name, api in apis.items():
        thread = threading.Thread(target=collect_user_ids, args=(conn_name, api))
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()
    
    end_time = time.time()
    print("\n\nTime elapsed: {} min".format((end_time - start_time)/60))
