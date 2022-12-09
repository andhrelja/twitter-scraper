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
batch = 1


def __collect_user_objs(conn_name, api, pbar):
    global q, l, batch
    while not q.empty():
        user_ids = q.get()
        user_objs = utils.get_twitter_lookup_users(conn_name, api, user_ids)
        user_objs = [user._json for user in user_objs]
        
        l.acquire()
        existing_users = fileio.read_content(settings.SCRAPE_USER_OBJS_FN.format(batch=batch), file_type='json')
        if len(existing_users) > 7_000:
            batch += 1
            
        fileio.write_content(
            path=settings.SCRAPE_USER_OBJS_FN.format(batch=batch), 
            content=user_objs, 
            file_type='json',
            indent=None
        )
        fileio.write_content(settings.PROCESSED_USER_OBJS, user_ids, 'json')
        l.release()
        pbar.update(1)


def user_objs(apis):
    global q

    start_time = dt.datetime.now(settings.TZ_INFO)
    utils.mkdir(os.path.dirname(settings.SCRAPE_USER_OBJS_FN))
    
    baseline_user_ids = utils.get_baseline_user_ids(processed_filepath=settings.PROCESSED_USER_OBJS)
    for user_ids in utils.batches(baseline_user_ids, 100):
        q.put(user_ids)
    
    logger.info("Scraping User objects")

    threads = []
    pbar = tqdm(total=q.qsize(), desc='scrape.user_objs', position=-1)
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
