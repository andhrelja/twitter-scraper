# %%
import os
import csv
import langid
import pandas as pd
import datetime as dt
from tqdm import tqdm

from twitter_scraper import utils
from twitter_scraper.utils import fileio
from twitter_scraper import settings

logger = utils.get_logger(__file__)

SCRAPE_TWEETS_DIR = os.path.dirname(settings.SCRAPE_TWEETS_FN)

MIN_DATE = dt.datetime.fromisoformat("2022-06-01T00:00:00+00:00")
MAX_DATE = dt.datetime.now(settings.TZ_INFO)
# MAX_DATE = dt.datetime.fromisoformat("2022-02-01T00:00:00+00:00")


flatten_dictlist = lambda dictlist, colname: [_dict.get(colname) for _dict in dictlist]
SCRAPE_TWEET = lambda x: {
    'id':                   x.get('id'),
    'user_id':              x.get('user', {}).get('id'),
    'user_id_str':          x.get('user', {}).get('id_str'),
    'full_text':            x.get('full_text') if not 'retweeted_status' in x else x['retweeted_status'].get('full_text'),
    'created_at':           x.get('created_at'),
    'hashtags':             flatten_dictlist(x.get('entities', {}).get('hashtags', []), 'text') if not 'retweeted_status' in x else flatten_dictlist(x['retweeted_status'].get('entities', {}).get('hashtags', []), 'text'),
    'user_mentions':        flatten_dictlist(x.get('entities', {}).get('user_mentions', []), 'id') if not 'retweeted_status' in x else flatten_dictlist(x['retweeted_status'].get('entities', {}).get('user_mentions', []), 'id'),
    'retweet_count':        x.get('retweet_count'),
    'retweet_from_user_id':         x.get('retweeted_status', {}).get('user', {}).get('id'),
    'retweet_from_tweet_id':        x.get('retweeted_status', {}).get('id'),
    'retweet_created_at':           x.get('retweeted_status', {}).get('created_at'),
	'in_reply_to_status_id':        x.get('in_reply_to_status_id'),
	'in_reply_to_status_id_str':    x.get('in_reply_to_status_id_str'),
	'in_reply_to_user_id':          x.get('in_reply_to_user_id'),
	'in_reply_to_user_id_str':      x.get('in_reply_to_user_id_str'),
	'in_reply_to_screen_name':      x.get('in_reply_to_screen_name'),
	# 'geo':                  x.get('geo'),
	# 'coordinates':          x.get('coordinates'),
	# 'place':                x.get('place'),
	# 'contributors':         x.get('contributors'),
	'is_quote_status':      x.get('is_quote_status'),
	'favorite_count':       x.get('favorite_count'),
	'favorited':            x.get('favorited'),
	'retweeted':            x.get('retweeted'),
	'possibly_sensitive':   x.get('possibly_sensitive'),
	'lang':                 x.get('lang')
}

TWEET_DTYPE = {
    'id':               'int64',
    'user_id':          'int64',
    # 'user_id_str':      'string',
    'full_text':        'string',
    'created_at':       'object',
    'hashtags':         'object',
    'user_mentions':    'object',
    'retweet_from_user_id':         pd.Int64Dtype(),
    # 'retweet_from_user_id_str':   'string',
    'retweet_from_tweet_id':        pd.Int64Dtype(),
    'retweet_created_at':           'object',
    'retweet_timedelta_sec':        pd.Int64Dtype(),
	'in_reply_to_status_id':        pd.Int64Dtype(),
	# 'in_reply_to_status_id_str':  'string',
	'in_reply_to_user_id':          pd.Int64Dtype(),
	# 'in_reply_to_user_id_str':    'string',
	# 'in_reply_to_screen_name':    'string',
	# 'geo':              'object',
	# 'coordinates':      'object',
	# 'place':          'object',
	# # 'contributors':   'object',
	# 'is_quote_status':  'bool',
    # 'retweet_count':    'int',
	'favorite_count':   'int',
	# 'favorited':        'bool',
	# 'retweeted':      'bool',
	'possibly_sensitive': 'bool',
	# 'lang':     'string',

    ### Custom columns
    'langid':   'string',
    'week':     'string',
    'month':    'string'
}

# %%
def detect_language(text):
    if text is None or text == '':
        return 'zxx'
    try:
        lang, _ = langid.classify(text)
    except Exception:
        lang = 'zxx'
    return lang


def transform(tweets_df):
    tweets_df['created_at'] = pd.to_datetime(tweets_df['created_at'], format='%a %b %d %H:%M:%S %z %Y')
    tweets_df = tweets_df.loc[
        (tweets_df['created_at'] >= MIN_DATE)
        & (tweets_df['created_at'] <= MAX_DATE)
    ].copy()
    
    tweets_df['retweet_created_at'] = pd.to_datetime(tweets_df['retweet_created_at'], format='%a %b %d %H:%M:%S %z %Y')
    tweets_df['retweet_timedelta_ns']   = tweets_df['created_at'] - tweets_df['retweet_created_at']
    tweets_df['retweet_timedelta_sec']  = tweets_df['retweet_timedelta_ns'].transform(lambda x: x.total_seconds())
    
    tweets_df['week']       = tweets_df['created_at'].dt.strftime('%Y-%W')
    tweets_df['month']      = tweets_df['created_at'].dt.strftime('%Y-%m')
    tweets_df['full_text']  = tweets_df['full_text'].fillna('')
    tweets_df['langid']     = tweets_df.apply(lambda x: detect_language(x['full_text']) if x['lang'] in ('und', 'zxx', 'pt') else x['lang'], axis=1)
    return tweets_df.astype(TWEET_DTYPE)


def get_tweets_df():
    logger.info("Reading raw Tweet json, this may take a while")
    
    all_tweets = []
    for file_name in tqdm(os.listdir(SCRAPE_TWEETS_DIR), desc='clean.tweets', position=-1):
        user_id = file_name.replace('.json', '')
        user_tweets = fileio.read_content(settings.SCRAPE_TWEETS_FN.format(user_id=user_id), 'json')
        all_tweets += [SCRAPE_TWEET(tweet) for tweet in user_tweets]
    
    logger.info("Transforming Tweet data, this may take a while")
    tweets_df = pd.DataFrame(all_tweets)
    tweets_df = transform(tweets_df)
    
    for file_name in tqdm(os.listdir(SCRAPE_TWEETS_DIR), desc='processed.tweets', position=-1):
        os.rename(
            src=os.path.join(SCRAPE_TWEETS_DIR, file_name), 
            dst=os.path.join(settings.PROCESSED_SCRAPE_TWEETS_DIR, file_name)
        )
    return tweets_df

# %%
def tweets():
    start_time = dt.datetime.now(settings.TZ_INFO)
    
    utils.mkdir(os.path.dirname(settings.CLEAN_TWEETS_CSV))
    
    logger.info("START - Cleaning Tweets")
    tweets_df = get_tweets_df()
    tweets_df.to_csv(
        settings.CLEAN_TWEETS_CSV, 
        index=False, 
        encoding='utf-8',
        quoting=csv.QUOTE_ALL
    )
    logger.info("Wrote Tweet model")
    
    end_time = dt.datetime.now(settings.TZ_INFO)
    logger.info("Tweet models saved: {}".format(settings.CLEAN_TWEETS_CSV))
    logger.info("END - Done cleaning Tweets")
    logger.info("Time elapsed: {} min".format(end_time - start_time))
    
# %%
if __name__ == '__main__':
    tweets()