import os
import time
import shutil
import queue
import threading
from tqdm import tqdm

from . import utils
from . import fileio
from twitter_scraper import settings

baseline_user_ids = utils.get_baseline_user_ids()
logger = utils.get_logger(__file__)

l = threading.Lock()
q = queue.Queue()


def archive_baseline(prefix=None):
    src = settings.BASELINE_USER_IDS
    baseline_path, baseline_name = os.path.split(settings.BASELINE_USER_IDS)
    utils.mkdir(os.path.join(baseline_path, 'history'))
    dst = os.path.join(
        baseline_path, 'history', 
        "_".join(filter(None, [prefix, settings.folder_name, baseline_name]))
    )
    
    shutil.copy(src, dst)
    logger.info("Baseline archived: {}".format(dst))


def update_user_friends_baseline():
    logger.info("`user_friends`")
    start_time = time.time()

    user_friends_ids = set()
    for user_id in tqdm(baseline_user_ids):
        file_name = f'{user_id}.json'
        file_path = os.path.join(settings.USER_IDS_DIR, file_name)
        
        file_content = fileio.read_content(file_path, file_type='json')
        if file_content: # TODO: sync input to output data
            user_friends_ids = user_friends_ids.union(file_content[str(user_id)]['friends'])
    
    user_friends_ids.difference_update(baseline_user_ids)
    logger.info("Appending {} `user_friends` to baseline".format(len(user_friends_ids)))
    fileio.write_content(settings.BASELINE_USER_IDS, list(user_friends_ids), file_type='json')
    logger.info("Updated baseline from {:,} to {:,} records".format(len(baseline_user_ids), len(user_friends_ids) + len(baseline_user_ids)))

    end_time = time.time()
    logger.info("Time elapsed: {} min".format(round((end_time - start_time)/60, 2)))


def update_user_mentions_baseline():
    global baseline_user_ids
    logger.info("`user_mentions`")
    start_time = time.time()

    user_mentions_ids = set()
    for file_name in tqdm(list(filter(lambda x: x.endswith('.json'), os.listdir(settings.USER_TWEETS_DIR)))):
        file_path = os.path.join(settings.USER_TWEETS_DIR, file_name)
        file_content = fileio.read_content(file_path, file_type='json')
        for tweet_obj in file_content:
            user_mentions_ids = user_mentions_ids.union(tweet_obj['user_mentions'])
    
    user_mentions_ids.difference_update(baseline_user_ids)
    logger.info("Appending {} `user_mentions` to baseline".format(len(user_mentions_ids)))
    fileio.write_content(settings.BASELINE_USER_IDS, list(user_mentions_ids), file_type='json')
    logger.info("Updated baseline from {:,} to {:,} records".format(len(baseline_user_ids), len(user_mentions_ids) + len(baseline_user_ids)))
    
    end_time = time.time()
    logger.info("Time elapsed: {} min".format(round((end_time - start_time)/60, 2)))


def update_user_retweets_baseline():
    global baseline_user_ids
    logger.info("`user_retweets`")
    start_time = time.time()

    user_retweet_ids = set()
    for file_name in tqdm(list(filter(lambda x: x.endswith('.json'), os.listdir(settings.USER_TWEETS_DIR)))):
        file_path = os.path.join(settings.USER_TWEETS_DIR, file_name)
        file_content = fileio.read_content(file_path, file_type='json')
        retweet_from_user_ids = list()
        for tweet_obj in filter(lambda x: x['retweet_from_user_id'] is not None, file_content):
            retweet_from_user_ids.append(tweet_obj['retweet_from_user_id'])
        user_retweet_ids = user_retweet_ids.union(retweet_from_user_ids)
    
    user_retweet_ids.difference_update(baseline_user_ids)
    logger.info("Appending {} `user_retweets` to baseline".format(len(user_retweet_ids)))
    fileio.write_content(settings.BASELINE_USER_IDS, list(user_retweet_ids), file_type='json')
    logger.info("Updated baseline from {:,} to {:,} records".format(len(baseline_user_ids), len(user_retweet_ids) + len(baseline_user_ids)))
    
    end_time = time.time()
    logger.info("Time elapsed: {} min".format(round((end_time - start_time)/60, 2)))


def update_baseline(archive=True, user_friends=True, user_mentions=True, user_retweets=True):
    if archive:
        archive_baseline(prefix='utils.update_baseline')
    if user_friends:
        update_user_friends_baseline()
    if user_mentions:
        update_user_mentions_baseline()
    if user_retweets:
        update_user_retweets_baseline()

if __name__ == '__main__':
    update_baseline(archive=True, user_friends=True, user_mentions=True, user_retweets=True)