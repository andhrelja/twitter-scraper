import os
import time
import shutil
import queue
import threading
import pandas as pd
from tqdm import tqdm

from twitter_scraper import settings
from twitter_scraper import utils
from twitter_scraper.utils import fileio
# from twitter_scraper.clean.tweets import TWEET_DTYPE

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
    baseline_user_ids = utils.get_baseline_user_ids()
    processed_user_ids = fileio.read_content(settings.PROCESSED_USER_OBJS, 'json')

    user_friends_ids = set()
    for user_id in tqdm(baseline_user_ids):
        file_name = f'{user_id}.json'
        file_path = os.path.join(settings.USER_IDS_DIR, file_name)
        
        file_content = fileio.read_content(file_path, file_type='json')
        if file_content: # TODO: sync input to output data
            user_friends_ids = user_friends_ids.union(file_content[str(user_id)]['friends'])
    
    user_friends_ids.difference_update(baseline_user_ids)
    user_friends_ids.difference_update(processed_user_ids)
    logger.info("Appending {} `user_friends` to baseline".format(len(user_friends_ids)))
    fileio.write_content(settings.BASELINE_USER_IDS, list(user_friends_ids), file_type='json')
    logger.info("Updated baseline from {:,} to {:,} records".format(len(baseline_user_ids), len(user_friends_ids) + len(baseline_user_ids)))

    end_time = time.time()
    logger.info("Time elapsed: {} min".format(round((end_time - start_time)/60, 2)))


def update_user_mentions_baseline(tweets_df):
    logger.info("`user_mentions`")
    start_time = time.time()
    baseline_user_ids = utils.get_baseline_user_ids()
    processed_user_ids = fileio.read_content(settings.PROCESSED_USER_OBJS, 'json')

    mentions_df = tweets_df[['user_id', 'user_mentions']][~tweets_df['user_mentions'].isna()]
    mentions_df = mentions_df[['user_id', 'user_mentions']].groupby('user_id').sum()
    mentions_df['user_mentions'] = mentions_df['user_mentions'].map(set)
    user_mentions_df = mentions_df.explode(column='user_mentions')
    
    user_mentions_ids = set(user_mentions_df[~user_mentions_df['user_mentions'].isna()].user_mentions.values)
    user_mentions_ids.difference_update(baseline_user_ids)
    user_mentions_ids.difference_update(processed_user_ids)

    logger.info("Appending {} `user_mentions` to baseline".format(len(user_mentions_ids)))
    fileio.write_content(settings.BASELINE_USER_IDS, list(map(int, user_mentions_ids)), file_type='json')
    logger.info("Updated baseline from {:,} to {:,} records".format(len(baseline_user_ids), len(user_mentions_ids) + len(baseline_user_ids)))
    
    end_time = time.time()
    logger.info("Time elapsed: {} min".format(round((end_time - start_time)/60, 2)))


def update_user_retweets_baseline(tweets_df):
    logger.info("`user_retweets`")
    start_time = time.time()
    baseline_user_ids = utils.get_baseline_user_ids()
    processed_user_ids = fileio.read_content(settings.PROCESSED_USER_OBJS, 'json')

    retweets_df = tweets_df[['user_id', 'retweet_from_user_id']][~tweets_df['retweet_from_user_id'].isna()]
    user_retweet_ids = set(retweets_df.retweet_from_user_id.values)
    user_retweet_ids.difference_update(baseline_user_ids)
    user_retweet_ids.difference_update(processed_user_ids)

    logger.info("Appending {} `user_retweets` to baseline".format(len(user_retweet_ids)))
    fileio.write_content(settings.BASELINE_USER_IDS, list(map(int, user_retweet_ids)), file_type='json')
    logger.info("Updated baseline from {:,} to {:,} records".format(len(baseline_user_ids), len(user_retweet_ids) + len(baseline_user_ids)))
    
    end_time = time.time()
    logger.info("Time elapsed: {} min".format(round((end_time - start_time)/60, 2)))


def update_baseline(archive=True, user_friends=True, user_mentions=True, user_retweets=True):
    tweets_df = pd.read_csv(settings.TWEETS_CSV)#, dtype=TWEET_DTYPE)
    tweets_df['user_mentions'] = tweets_df['user_mentions'].map(eval)
    if archive:
        archive_baseline(prefix='utils.update_baseline')
    if user_friends:
        update_user_friends_baseline()
    if user_mentions:
        update_user_mentions_baseline(tweets_df)
    if user_retweets:
        update_user_retweets_baseline(tweets_df)

if __name__ == '__main__':
    update_baseline(archive=True, user_friends=False, user_mentions=True, user_retweets=True)