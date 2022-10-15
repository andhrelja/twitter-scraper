import os
import pandas as pd

from twitter_scraper import utils
from twitter_scraper import settings

def processed_objs_matches_user_objs():
    processed_user_objs = utils.fileio.read_content(settings.PROCESSED_USER_OBJS, 'json')
    missing_user_objs = utils.fileio.read_content(settings.MISSING_USER_IDS, 'json')
    user_objs_df = pd.read_csv(os.path.join(settings.USER_OBJS_DIR, 'user-objs.csv'))
    assert len(processed_user_objs) == len(set(list(user_objs_df.user_id) + missing_user_objs))

def clean_users_matches_user_ids():
    users_df = pd.read_csv(settings.USERS_CSV)
    user_ids = os.listdir(settings.USER_IDS_DIR)
    assert len(users_df) == len(user_ids)

def clean_tweets_matches_user_ids():
    tweet_ids = os.listdir(settings.USER_TWEETS_DIR)
    user_ids = os.listdir(settings.USER_IDS_DIR)
    assert len(tweet_ids) == len(user_ids)
