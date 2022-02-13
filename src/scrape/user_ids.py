import os
import time
import shutil
import queue
import threading
from tqdm import tqdm

import utils
import utils.fileio as fileio
from twitter_scraper import settings

logger = utils.get_logger(__file__)

l = threading.Lock()
q = queue.Queue()

baseline_user_ids = utils.get_baseline_user_ids(processed_filepath=settings.PROCESSED_USER_IDS)


def collect_user_ids(conn_name, api, pbar):
    global q, l, baseline_user_ids
    
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


def _update_baseline(pbar):   
    """update_baseline

    Reads through collected user ids and merges 
    their followers to baseline_user_id
    
    Returns:
        List[int]: updated list of baseline user ids
    """
    global q, l
    
    all_user_ids = set()
    content = {}
    
    while not q.empty():
        user_id = q.get()
        user = fileio.read_content(os.path.join(settings.USER_IDS_DIR, '{}.json'.format(user_id)), 'json')
        if user:
            all_user_ids = all_user_ids.union(
                [user_id] + user[str(user_id)]['followers']
            )
            content.update(user)
        pbar.update(1)

    
    all_user_ids = all_user_ids.difference(baseline_user_ids)
    
    l.acquire()
    fileio.write_content(settings.BASELINE_USER_IDS, list(all_user_ids), 'json')
    l.release()


def update_baseline():
    logger.info("Updating baseline")
    
    def move_baseline():
        src = settings.BASELINE_USER_IDS
        baseline_path, baseline_name = os.path.split(settings.BASELINE_USER_IDS)
        dst = os.path.join(
            baseline_path, 'history', 
            "_".join([settings.folder_name, baseline_name])
        )
        
        shutil.copy(src, dst)
    move_baseline()
    
    global q, baseline
    baseline_user_ids = utils.get_baseline_user_ids()
    start_time = time.time()
    q = queue.Queue()
    
    threads = []
    for user_id in baseline_user_ids:
        q.put(user_id)
    
    logger.info("Reading user's friends and followers")
    pbar = tqdm(total=len(os.listdir(settings.USER_IDS_DIR)))
    
    for _ in range(4):
        thread = threading.Thread(
            target=_update_baseline, 
            args=(pbar,)
        )
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()
    
    pbar.close()
    end_time = time.time()
    logger.info("Time elapsed: {} min".format((end_time - start_time)/60))


def user_ids(apis):
    # 15 000 users in 28h
    global q, baseline_user_ids
    start_time = time.time()
    if not os.path.exists(settings.USER_IDS_DIR):
        os.mkdir(settings.USER_IDS_DIR)
    
    if settings.DEBUG:
        limit = 10
        baseline_user_ids = list(baseline_user_ids)[:limit]
    
    threads = []
    for user_id in baseline_user_ids:
        q.put(user_id)
    
    logger.info("Scraping User IDs")
    pbar = tqdm(total=len(baseline_user_ids))
    
    for conn_name, api in apis.items():
        thread = threading.Thread(
            target=collect_user_ids, 
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
    user_ids(apis)
    #update_baseline()