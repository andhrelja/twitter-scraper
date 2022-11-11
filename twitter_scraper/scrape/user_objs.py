import os
import queue
import threading
import datetime as dt
from tqdm import tqdm

from twitter_scraper import utils
from twitter_scraper.utils import fileio
from twitter_scraper import settings

logger = utils.get_logger(__file__)

l = threading.Lock()
q = queue.Queue()

SCRAPE_USER = lambda x: {
    'user_id':          x.get('id'),
    'user_id_str':      x.get('id_str'),
    'name':             x.get('name'),
    'screen_name':      x.get('screen_name'),
    'location':         x.get('location'),
    "profile_location": x.get('profile_location'),
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


def __collect_user_objs(conn_name, api, pbar):
    global q, l
    while not q.empty():
        user_ids = q.get()
        user_objs = utils.get_twitter_lookup_users(conn_name, api, user_ids)
        user_objs = [SCRAPE_USER(user._json) for user in user_objs]
        
        l.acquire()
        fileio.write_content(
            path=settings.SCRAPE_USER_OBJS_FN, 
            content=user_objs, 
            file_type='json'
        )
        fileio.write_content(settings.PROCESSED_USER_OBJS, user_ids, 'json')
        l.release()
        pbar.update(1)


def user_objs(apis):
    global q

    start_time = dt.datetime.now(settings.TZ_INFO)
    utils.mkdir(os.path.dirname(settings.SCRAPE_USER_OBJS_FN))
    
    baseline_user_ids = utils.get_baseline_user_ids(processed_filepath=settings.PROCESSED_USER_OBJS)
    user_id_batches = utils.batches(list(baseline_user_ids), 100)
    for user_ids in user_id_batches:
        q.put(user_ids)
    
    logger.info("Scraping User objects")

    threads = []
    pbar = tqdm(total=len(user_id_batches), desc='scrape.user_objs', position=-1)
    for conn_name, api in apis.items():
        thread = threading.Thread(
            target=__collect_user_objs, 
            args=(conn_name, api, pbar)
        )
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()
    pbar.close()
    
    end_time = dt.datetime.now(settings.TZ_INFO)
    logger.info("Time elapsed: {} min".format(end_time - start_time))


if __name__ == '__main__':
    apis = utils.get_api_connections()
    user_objs(apis)
