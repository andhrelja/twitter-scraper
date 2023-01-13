# %%
import os
import csv
import pandas as pd
import datetime as dt
from tqdm import tqdm

from twitter_scraper import utils
from twitter_scraper.utils import fileio
from twitter_scraper import settings

logger = utils.get_logger(__file__)

MIN_DATE = dt.datetime.fromisoformat("2022-10-01T00:00:00+00:00")
MAX_DATE = dt.datetime.now(settings.TZ_INFO)
# MAX_DATE = dt.datetime.fromisoformat("2022-02-01T00:00:00+00:00")

flatten_dictlist = lambda dictlist, key: [_dict.get(key) for _dict in dictlist]

# %%
def transform(tweets_df, folder_name=settings.folder_name):
    tweets_df['created_at'] = pd.to_datetime(tweets_df['created_at'], format='%a %b %d %H:%M:%S %z %Y')
    tweets_df = tweets_df.loc[
        (tweets_df['created_at'] >= MIN_DATE)
        & (tweets_df['created_at'] <= MAX_DATE)
    ].drop_duplicates(subset='id').copy()
    
    tweets_df['is_retweet'] = tweets_df['retweet_from_status_id'].notna()
    tweets_df['is_reply']   = tweets_df['in_reply_to_status_id'].notna()
    tweets_df['is_quote']   = tweets_df['is_quote_status']
    tweets_df['is_original'] = ~tweets_df['is_retweet'] # is_original
    
    # Mentions ## - users do not mention each other unless they reply to the post
    # user_mentions_gdf = tweets_df.explode('original_user_mentions').dropna(subset='original_user_mentions')
    # user_mentions_gdf = user_mentions_gdf[(user_mentions_gdf['screen_name'] != user_mentions_gdf['original_user_mentions']) & (user_mentions_gdf['is_reply'] == False)]
    # user_mentions_gdf = user_mentions_gdf.groupby('original_user_mentions').agg(original_user_mentions_cnt=('original_user_mentions', 'size'))
    # tweets_df['user_mentions_cnt'] = tweets_df['screen_name'].transform(lambda x: user_mentions_gdf.original_user_mentions_cnt.get(x, 0))
    
    # Retweets
    tweets_df['retweet_created_at'] = pd.to_datetime(tweets_df['retweet_created_at'], format='%a %b %d %H:%M:%S %z %Y')
    tweets_df['retweet_timedelta_ns']   = tweets_df['created_at'] - tweets_df['retweet_created_at']
    tweets_df['retweet_timedelta_sec']  = tweets_df['retweet_timedelta_ns'].transform(lambda x: x.total_seconds())
    retweets_size_gdf = tweets_df.groupby('retweet_from_status_id').agg(
        in_retweet_cnt=('retweet_from_status_id', 'size'),
        in_retweet_timedelta_sec=('retweet_timedelta_sec', 'mean')
    )
    tweets_df['in_retweet_cnt'] = tweets_df['id'].transform(lambda x: retweets_size_gdf.in_retweet_cnt.get(x, 0))
    tweets_df['in_retweet_timedelta_sec'] = tweets_df['id'].transform(lambda x: retweets_size_gdf.in_retweet_timedelta_sec.get(x, 0))
    
    
    # Quotes
    tweets_df['quote_created_at'] = pd.to_datetime(tweets_df['quote_created_at'], format='%a %b %d %H:%M:%S %z %Y')
    tweets_df['quote_timedelta_ns']   = tweets_df['created_at'] - tweets_df['quote_created_at']
    tweets_df['quote_timedelta_sec']  = tweets_df['quote_timedelta_ns'].transform(lambda x: x.total_seconds())
    quote_size_gdf = tweets_df.groupby('quote_from_status_id').agg(
        in_quote_cnt=('quote_from_status_id', 'size'),
        in_quote_timedelta_sec=('quote_timedelta_sec', 'mean')
    )
    tweets_df['in_quote_cnt'] = tweets_df['id'].transform(lambda x: quote_size_gdf.in_quote_cnt.get(x, 0))
    tweets_df['in_quote_timedelta_sec'] = tweets_df['id'].transform(lambda x: quote_size_gdf.in_quote_timedelta_sec.get(x, 0))
    
    
    # Replies
    reply_size_gdf = tweets_df.groupby('in_reply_to_status_id').agg(in_reply_cnt=('in_reply_to_status_id', 'size'))
    tweets_df['in_reply_cnt'] = tweets_df['id'].transform(lambda x: reply_size_gdf.in_reply_cnt.get(x, 0))

    ## Tweet Date & Time
    tweets_df['year']       = tweets_df['created_at'].dt.year
    tweets_df['quarter']    = tweets_df['created_at'].dt.quarter
    tweets_df['quarter_name'] = tweets_df['created_at'].transform(lambda x: "{}Q{}".format(x.year, x.quarter))
    tweets_df['month']      = tweets_df['created_at'].dt.month
    tweets_df['month_name'] = tweets_df['created_at'].dt.strftime('%Y-%m')
    tweets_df['week']       = tweets_df['created_at'].dt.isocalendar().week
    tweets_df['week_name']  = tweets_df['created_at'].dt.strftime('%Y-%W')
    tweets_df['day']        = tweets_df['created_at'].dt.day
    tweets_df['day_name']   = tweets_df['created_at'].dt.strftime('%Y-%m-%d')
    tweets_df['hour']       = tweets_df['created_at'].dt.hour
    tweets_df['minute']     = tweets_df['created_at'].dt.minute
    tweets_df['second']     = tweets_df['created_at'].dt.second
    
    tweets_df['full_text']  = tweets_df['full_text'].fillna('')
    tweets_df['folder_name'] = folder_name
    return tweets_df.astype(TWEET_DTYPE)

# %%
SCRAPE_TWEET = lambda x: {
    'id':                  x.get('id'),
    'user_id':             x.get('user', {}).get('id'),
    'user_id_str':         x.get('user', {}).get('id_str'),
    'full_text':           x.get('retweeted_status', {}).get('full_text', x.get('full_text')) 
                            + '\n\n' + x.get('retweeted_status', {}).get('full_text', x.get('full_text')),
    'created_at':          x.get('created_at'),
    'favorite_count':      x.get('favorite_count'),
	'possibly_sensitive':  x.get('possibly_sensitive'),
 
    'hashtags':            flatten_dictlist(x.get('entities', {}).get('hashtags', []), 'text'),
    'user_mentions':       flatten_dictlist(x.get('entities', {}).get('user_mentions', []), 'screen_name'),
    'user_mentions_ids':   flatten_dictlist(x.get('entities', {}).get('user_mentions', []), 'id'),
    
    # Hashtags Transform
    'original_hashtags': flatten_dictlist(x.get('entities', {}).get('hashtags', []), 'text') \
                         if not x.get('retweeted_status') else list(),
    'retweet_hashtags': flatten_dictlist(
                        x.get('retweeted_status', {}).get('entities', {}).get('hashtags', []), 'text') \
                        if x.get('retweeted_status') else list(),
    'quote_hashtags': flatten_dictlist(
                      x.get('quoted_status', {}).get('entities', {}).get('hashtags', []), 'text') \
                      if x['is_quote_status'] is True else list(),
    
    # User mentions Transform
    'original_user_mentions': flatten_dictlist(x.get('entities', {}).get('user_mentions', []), 'screen_name')
                              if not x.get('retweeted_status') else list(),
    'retweet_user_mentions': flatten_dictlist(
                             x.get('retweeted_status', {}).get('entities', {}).get('user_mentions', []), 'screen_name') \
                             if x.get('retweeted_status') else list(),
    'quote_user_mentions': flatten_dictlist(
                           x.get('quoted_status', {}).get('entities', {}).get('user_mentions', []), 'screen_name') \
                           if x['is_quote_status'] is True else list(),
    
    'original_favorite_cnt':        x.get('favorite_count', 0),
    
    # 'retweet_count':                x.get('retweet_count'), # aggregated measure
    'retweet_from_user_id':         x.get('retweeted_status', {}).get('user', {}).get('id'),
    'retweet_from_screen_name':     x.get('retweeted_status', {}).get('user', {}).get('screen_name'),
    'retweet_from_status_id':       x.get('retweeted_status', {}).get('id'),
    'retweet_created_at':           x.get('retweeted_status', {}).get('created_at'),
    'retweet_favorite_cnt':         x.get('retweeted_status', {}).get('favorite_count'),
    
    'is_quote_status':              x.get('is_quote_status'),
    'quote_from_user_id':           x.get('quoted_status', {}).get('user', {}).get('id'),
    'quote_from_screen_name':       x.get('quoted_status', {}).get('user', {}).get('screen_name'),
    'quote_from_status_id':         x.get('quoted_status', {}).get('id'),
    'quote_created_at':             x.get('quoted_status', {}).get('created_at'),
    'quote_favorite_cnt':           x.get('quoted_status', {}).get('favorite_count'),
    
	'in_reply_to_status_id':        x.get('in_reply_to_status_id'),
	'in_reply_to_status_id_str':    x.get('in_reply_to_status_id_str'),
	'in_reply_to_user_id':          x.get('in_reply_to_user_id'),
	'in_reply_to_user_id_str':      x.get('in_reply_to_user_id_str'),
	'in_reply_to_screen_name':      x.get('in_reply_to_screen_name'),   

	# 'favorited':                    x.get('favorited'), boolean based on the authenticating user
	# 'retweeted':                    x.get('retweeted'), boolean based on the authenticating user
 
	'lang':                         x.get('lang'),
    'folder_name':                  settings.folder_name
}


TWEET_DTYPE = {
    # Tweet
	'id':							'int64',
    'folder_name':                  'string',
	'user_id':						'int64',
    'user_id_str':					'string',
	'full_text':					'string',
    'lang':							'category',
    'possibly_sensitive':			'boolean',
    
    'hashtags':				        'object',
    'user_mentions':				'object',
    'user_mentions_ids':			'object',
    
    ## Tweet Date & Time
	'created_at':					'object',
    'year':                         'int',
    'quarter':                      'int',
    'quarter_name':                 'string',
    'month':                        'int',
    'month_name':                   'string',
    'week':                         'int',
    'week_name':                    'string',
    'day':                          'int',
    'day_name':                     'string',
    'hour':                         'int',
    'minute':                       'int',
    'second':                       'int',
    
    ## Tweets
    'original_hashtags':			'object',
    'retweet_hashtags':				'object',
    'quote_hashtags':				'object',
    
    # Original Tweets
    'is_original':                  'boolean', # !is_retweet
    'original_favorite_cnt':        'int',
    
	# Retweets
	'is_retweet':					'boolean',
    'retweet_favorite_cnt':	        'Int64', # nullable
    'in_retweet_cnt':               'int', # !! important: calculate while transforming
    'in_retweet_timedelta_sec':     'float', # !! important: calculate while transforming
    'retweet_created_at':			'object', # nullable
	'retweet_from_user_id':			'Int64', # nullable
    'retweet_from_screen_name':		'string', # nullable
	'retweet_from_status_id':		'Int64', # nullable
    'retweet_timedelta_sec':        'Int64', # nullable
	
    # Quotes
    'is_quote':				        'boolean',
    'quote_favorite_cnt':	        'Int64', # nullable
    'in_quote_cnt':                 'int', # !! important: calculate while transforming    
    'in_quote_timedelta_sec':       'float', # !! important: calculate while transforming    
    'quote_created_at':             'object', # nullable
    'quote_from_user_id':           'Int64', # nullable
    'quote_from_screen_name':       'string', # nullable
    'quote_from_status_id':         'Int64', # nullable
    'quote_timedelta_sec':          'Int64',  # nullable

    
    # Replies
	'is_reply':						'boolean',
    'in_reply_cnt':                 'int',
	'in_reply_to_user_id':			'Int64', # nullable 
	'in_reply_to_status_id':		'Int64', # nullable
	'in_reply_to_screen_name':		'string', # nullable
 
}

# %%
def tweets():
    start_time = dt.datetime.now(settings.TZ_INFO)
    
    utils.mkdir(os.path.dirname(settings.CLEAN_TWEETS_CSV))
    
    logger.info("START - Cleaning Tweets")
    logger.info("Reading raw Tweet json, this may take a while")
    
    all_tweets = []
    for file_name in tqdm(os.listdir(os.path.dirname(settings.SCRAPE_TWEETS_FN)), desc='clean.tweets'):
        user_id = file_name.replace('.json', '')
        user_tweets = fileio.read_content(settings.SCRAPE_TWEETS_FN.format(user_id=user_id), 'json')
        all_tweets += [SCRAPE_TWEET(tweet) for tweet in user_tweets]
        # all_tweets += user_tweets

    logger.info("Transforming Tweet data, this may take a while")
    tweets_df = pd.DataFrame(all_tweets)
    tweets_df = transform(tweets_df)
    tweets_df.to_csv(
        settings.CLEAN_TWEETS_CSV, 
        index=False, 
        encoding='utf-8',
        quoting=csv.QUOTE_ALL
    )
    
    logger.info("END - Done cleaning Tweets. Model saved: {}".format(settings.CLEAN_TWEETS_CSV))
    
    end_time = dt.datetime.now(settings.TZ_INFO)
    logger.info("Time elapsed: {} min".format(end_time - start_time))
    
# %%
if __name__ == '__main__':
    tweets()
