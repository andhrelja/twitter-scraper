"""
clean.tweets
============

**Input**: ``~/data/output/scrape/tweets/<user-id>.json``

**Output**: ``~/data/output/clean/tweet/YYYY-MM-DD/tweets.csv``

Filter Tweets from 2021-08-01 onwards.

Conforms Tweet data to the following :module:pandas schema:

.. code-block:: python

    TWEET_DTYPE = {
        'id':               'string',
        'user_id':          'int64',
        'user_id_str':      'string',
        'full_text':        'string',
        'created_at':       'object',
        'hashtags':         'object',
        'user_mentions':    'object',
        'retweet_from_user_id':     'int64',
        'retweet_from_user_id_str': 'string',
        #'in_reply_to_status_id':      pd.Int64Dtype(),
        # 'in_reply_to_status_id_str':  'string',
        #'in_reply_to_user_id':        pd.Int64Dtype(),
        # 'in_reply_to_user_id_str':    'string',
        # 'in_reply_to_screen_name':    'string',
        'geo':              'object',
        'coordinates':      'object',
        # 'place':          'object',
        # 'contributors':   'object',
        # 'is_quote_status': 'bool',
        'retweet_count':    'int',
        'favorite_count':   'int',
        # 'favorited':      'bool',
        # 'retweeted':      'bool',
        # 'possibly_sensitive': 'bool',
        # 'lang': 'string',

        ### Custom columns
        'week': 'string',
        'month': 'string',
        'is_covid': 'bool'
    }

"""
# %%
import os
import time
import csv
import pandas as pd
import datetime as dt
from tqdm import tqdm

from twitter_scraper import utils
from twitter_scraper.utils import fileio
from twitter_scraper import settings

logger = utils.get_logger(__file__)

MIN_DATE = dt.datetime(2021, 8, 1, 0, 0, 0, 0, dt.timezone.utc)
# MAX_DATE = dt.datetime(2022, 1, 31, 0, 0, 0, 0, dt.timezone.utc)
MAX_DATE = dt.datetime.now(dt.timezone.utc)


TWEET_DTYPE = {
    'id':               'string',
    'user_id':          'int64',
    'user_id_str':      'string',
    'full_text':        'string',
    'created_at':       'object',
    'hashtags':         'object',
    'user_mentions':    'object',
    'retweet_from_user_id':     pd.Int64Dtype(),
    'retweet_from_user_id_str': 'string',
	#'in_reply_to_status_id':      pd.Int64Dtype(),
	# 'in_reply_to_status_id_str':  'string',
	#'in_reply_to_user_id':        pd.Int64Dtype(),
	# 'in_reply_to_user_id_str':    'string',
	# 'in_reply_to_screen_name':    'string',
	'geo':              'object',
	'coordinates':      'object',
	# 'place':          'object',
	# 'contributors':   'object',
	# 'is_quote_status': 'bool',
    'retweet_count':    'int',
	'favorite_count':   'int',
	# 'favorited':      'bool',
	# 'retweeted':      'bool',
	# 'possibly_sensitive': 'bool',
	# 'lang': 'string',

    ### Custom columns
    'week': 'string',
    'month': 'string',
    'is_covid': 'bool'
}


# %%
def get_tweets_df(user_df):
    def transform(tweets_df):
        tweets_df['week']  = tweets_df['created_at'].dt.strftime('%Y-%W')
        tweets_df['month'] = tweets_df['created_at'].dt.strftime('%Y-%m')
        
        tweets_df['hashtags']   = tweets_df['hashtags'].transform(lambda x: [item.lower() for item in x])
        tweets_df['full_text']  = tweets_df['full_text'].fillna('')
        tweets_df['full_text_nospace'] = tweets_df['full_text'].str.replace(' ', '')
        
        tweets_df['is_covid_1'] = tweets_df['full_text'].transform(lambda x: any(tag in x.lower()
                                                            for tag in settings.KEYWORDS['is_covid']))
        tweets_df['is_covid_2'] = tweets_df['full_text_nospace'].transform(lambda x: any(tag.replace(' ', '') in x.lower()
                                                            for tag in settings.KEYWORDS['is_covid']))
        tweets_df['is_covid_3'] = tweets_df['hashtags'].transform(lambda x: any(tag in x
                                                            for tag in settings.KEYWORDS['is_covid']))    
        
        tweets_df['is_covid'] = tweets_df['is_covid_1'] | tweets_df['is_covid_2'] | tweets_df['is_covid_3']
        return tweets_df[TWEET_DTYPE.keys()]
    
    logger.info("Reading raw Tweet json, this may take a while")
    data = []

    for user_id in tqdm(user_df.user_id_str.unique()):
        fn = '{}.json'.format(user_id)
        content = fileio.read_content(os.path.join(settings.USER_TWEETS_DIR, fn), 'json')
        data += content

    logger.info("Transforming Tweet data, this may take a while")
    tweets_df = pd.DataFrame(data)
    tweets_df['created_at'] = pd.to_datetime(tweets_df['created_at'], format='%a %b %d %H:%M:%S %z %Y')
    tweets_df = tweets_df[
        (tweets_df['created_at'] > MIN_DATE)
        & (tweets_df['created_at'] < MAX_DATE)
    ]
    
    tweets_df = transform(tweets_df)
    return tweets_df.astype(TWEET_DTYPE)

# %%
def tweets():
    start_time = time.time()
    
    utils.mkdir(os.path.dirname(settings.TWEETS_CSV))
    utils.mkdir(os.path.dirname(settings.NODES_CSV))
    utils.mkdir(os.path.dirname(settings.EDGES_FOLLOWERS_CSV))

    logger.info("START - Cleaning Tweets")
    user_df = pd.read_csv(settings.USERS_CSV, encoding='utf-8')
    tweets_df = get_tweets_df(user_df)

    tweets_df.to_csv(settings.TWEETS_CSV, index=False, quoting=csv.QUOTE_ALL)
    logger.info("Wrote Tweet model")
    
    end_time = time.time()
    logger.info("Tweet model saved: {}".format(settings.TWEETS_CSV))
    logger.info("END - Done cleaning Tweets")
    logger.info("Time elapsed: {} min".format(round((end_time - start_time)/60, 2)))
    
# %%
if __name__ == '__main__':
    tweets()