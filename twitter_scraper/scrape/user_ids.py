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


def __collect_user_ids(conn_name, api, pbar):
    global q, l
    
    while not q.empty():
        user_id = q.get()

        friend_ids, missing_user = utils.get_twitter_endpoint(conn_name, api, 'get_friend_ids', user_id)
        if missing_user and not friend_ids:
            l.acquire()
            fileio.write_content(settings.MISSING_USER_IDS, int(missing_user), 'json')
            l.release()
            pbar.update(1)
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
        fileio.write_content(settings.SCRAPE_USER_IDS_FN.format(user_id=user_id), output_dict, 'json', overwrite=True)
        fileio.write_content(settings.PROCESSED_USER_IDS, user_id, 'json')
        l.release()
        pbar.update(1)
    if os.path.exists(settings.PROCESSED_USER_IDS):
        os.remove(settings.PROCESSED_USER_IDS)
        logger.info("Deleted {}".format(settings.PROCESSED_USER_IDS))


def user_ids(apis):
    # 15 requests per connection
    # 15 min wait until new requests are available
    # 15*9=135 users per connection
    # 135 users / 3 sec
    # 15 000 users in 28h
    # 35 000 users in 65h
    
    global q

    start_time = dt.datetime.now(settings.TZ_INFO)
    threads = []
    
    utils.mkdir(os.path.dirname(settings.SCRAPE_USER_IDS_FN))
    
    processed_user_ids= fileio.read_content(settings.PROCESSED_USER_IDS, 'json')
    baseline_user_ids = fileio.read_content(settings.NODES_CSV, 'csv', column='user_id')
    for user_id in baseline_user_ids:
        q.put(user_id)
    
    logger.info("Scraping User IDs")

    pbar = tqdm(total=len(baseline_user_ids), desc='scrape.user_ids', position=-1)
    for conn_name, api in apis.items():
        thread = threading.Thread(
            target=__collect_user_ids, 
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
    user_ids(apis)