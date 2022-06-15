from ctypes import util
import os
import time
import shutil
import queue
import threading
import pandas as pd
from tqdm import tqdm

import utils
from utils import fileio
from twitter_scraper import settings
from clean.users import USER_DTYPE

logger = utils.get_logger(__file__)

l = threading.Lock()
q = queue.Queue()

baseline_user_ids = utils.get_baseline_user_ids()


def archive_baseline():
    src = settings.BASELINE_USER_IDS
    baseline_path, baseline_name = os.path.split(settings.BASELINE_USER_IDS)
    utils.mkdir(os.path.join(baseline_path, 'history'))
    dst = os.path.join(
        baseline_path, 'history', 
        "_".join([settings.folder_name, baseline_name])
    )
    
    shutil.copy(src, dst)
    logger.info("Baseline archived: {}".format(dst))


def clean_baseline():
    users_df = pd.read_csv(settings.USERS_CSV, dtype=USER_DTYPE)
    users_df = users_df[users_df['is_croatian'] == True]
    baseline_user_ids = set(fileio.read_content(settings.BASELINE_USER_IDS, 'json'))
    baseline_user_ids = baseline_user_ids.union(users_df.user_id.values)
    fileio.write_content(settings.BASELINE_USER_IDS, list(baseline_user_ids), 'json', overwrite=True)



def __user_followers(pbar):
    """__user_followers

    Reads through collected user ids and merges 
    their followers to baseline_user_id
    
    Appends unionied list of updated baseline user ids
    to `~/data/input/baseline_user_ids.json
    """
    global q, l, baseline_user_ids
    all_user_ids = set()
    
    while not q.empty():
        user_id = q.get()
        user = fileio.read_content(os.path.join(settings.USER_IDS_DIR, '{}.json'.format(user_id)), 'json')
        if user:
            all_user_ids = all_user_ids.union(
                [user_id] + user[str(user_id)]['followers']
            )
        pbar.update(1)

    l.acquire()
    fileio.write_content(settings.BASELINE_USER_IDS, list(all_user_ids.difference(baseline_user_ids)), 'json')
    l.release()


def user_followers_baseline():
    global q, baseline_user_ids
    
    start_time = time.time()
    threads = []

    for user_id in baseline_user_ids:
        q.put(user_id)
    
    logger.info("Updating baseline - reading user's friends and followers")

    pbar = tqdm(total=len(os.listdir(settings.USER_IDS_DIR)))
    for _ in range(8):
        thread = threading.Thread(
            target=__user_followers, 
            args=(pbar,)
        )
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()
    pbar.close()

    end_time = time.time()
    logger.info("Time elapsed: {} min".format(round((end_time - start_time)/60, 2)))


def update_baseline(archive=True, clean=True, update=True):
    if archive:
        archive_baseline()
    if clean:
        clean_baseline()
    if update:
        user_followers_baseline()

if __name__ == '__main__':
    update_baseline(archive=True, clean=True, update=True)