import os
import time
import queue
import threading
from tqdm import tqdm

import utils
import utils.fileio as fileio
from twitter_scraper import settings

logger = utils.get_logger(__file__)

l = threading.Lock()
q = queue.Queue()

baseline_user_ids = utils.get_baseline_user_ids(processed_filepath=settings.PROCESSED_USER_OBJS)

SCRAPE_USER = lambda x: {
    'user_id':          x.get('id'),
    'user_id_str':      x.get('id_str'),
    'name':             x.get('name'),
    'screen_name':      x.get('screen_name'),
    'location':         x.get('location'),
    'derived':          x.get('derived'),
    'url':              x.get('url'),
    'description':      x.get('description'),
    'protected':        x.get('protected'),
    'verified':         x.get('verified'),
    'followers_count':  x.get('followers_count'),
    'friends_count':    x.get('friends_count'),
    'listed_count':     x.get('listed_count'),
    'favourites_count': x.get('favourites_count'),
    'statuses_count':   x.get('statuses_count'),
    'created_at':       x.get('created_at'),
    'profile_banner_url':      x.get('profile_banner_url'),
    'profile_image_url_https': x.get('profile_image_url_https'),
    'default_profile':         x.get('default_profile'),
    'default_profile_image':   x.get('default_profile_image'),
    'withheld_in_countries':   x.get('withheld_in_countries'),
    'withheld_scope':          x.get('withheld_scope'),
}


def collect_user_objs(conn_name, api, pbar):
    global q, l
    while not q.empty():
        pbar.update(1)
        user_ids = q.get()
        user_objs = utils.get_twitter_lookup_users(conn_name, api, user_ids)
        user_objs = [SCRAPE_USER(user._json) for user in user_objs]
        
        l.acquire()
        fileio.write_content(
            os.path.join(settings.USER_OBJS_DIR, 'user-objs.csv'), 
            user_objs, 'csv', 
            fieldnames=SCRAPE_USER({}).keys()
        )
        fileio.write_content(settings.PROCESSED_USER_OBJS, user_ids, 'json')
        l.release()


def user_objs(apis):
    global q, baseline_user_ids
    start_time = time.time()
    utils.mkdir(settings.USER_OBJS_DIR)

    threads = []
    user_id_batches = utils.batches(list(baseline_user_ids), 100)
    for user_ids in user_id_batches:
        q.put(user_ids)
    
    logger.info("Scraping User objects")
    pbar = tqdm(total=len(user_id_batches))
    
    for conn_name, api in apis.items():
        thread = threading.Thread(
            target=collect_user_objs, 
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
    user_objs(apis)