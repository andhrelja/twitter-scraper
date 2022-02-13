import os
import sys
import logging

from . import fileio
from twitter_scraper import settings


def get_logger(logger_name, **kwargs):
    path, logger_filename = os.path.split(logger_name)
    _, logger_module = os.path.split(path)
    logger_name = '{}.{}'.format(logger_module, logger_filename.replace('.py', ''))
    logging.basicConfig(
        format='[%(levelname)s] %(asctime)s %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.INFO,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(os.path.join(settings.LOGS_DIR, '{}.log'.format(settings.folder_name)))
        ],
        **kwargs
    )

    return logging.getLogger(logger_name)


def batches(lst, n=100):
    batches = []
    for i in range(0, len(lst), n):
        batches.append(lst[i:i+n])
    return batches


def get_tweet_max_id(user_id):
    user_tweets = fileio.read_content(os.path.join(settings.USER_TWEETS_DIR, '{}.json'.format(user_id)), 'json')
    if user_tweets:
        latest_tweet = max(user_tweets, key=lambda x: x['id'])
        return latest_tweet['id']
    return None


def get_baseline_user_ids(processed_filepath=None):
    baseline_user_ids = set(fileio.read_content(settings.BASELINE_USER_IDS, 'json'))       
    missing_user_ids = set(fileio.read_content(settings.MISSING_USER_IDS, 'json'))
    
    baseline_user_ids.difference_update(missing_user_ids)
    if processed_filepath is None:
        return baseline_user_ids
    
    processed_user_ids = set(fileio.read_content(processed_filepath, 'json'))
    baseline_user_ids.difference_update(processed_user_ids)
    return baseline_user_ids
