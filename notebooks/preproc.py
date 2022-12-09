from twitter_scraper.clean.users import USER_DTYPE
from twitter_scraper.clean.tweets import TWEET_DTYPE
from twitter_scraper import settings
from twitter_scraper import utils

import datetime as dt
import pandas as pd
import csv


ANALYSIS_MIN_DATE = dt.datetime.fromisoformat('2022-10-01T00:00:00+00:00')
ANALYSIS_COLUMNS = {
    # Tweet
    'tweets': [
        'id', 'full_text', 
        'created_at', 'year', 
        'quarter', 'quarter_name',
        'month', 'month_name',
        'week', 'week_name', 
        'day', 'day_name',
        'hour', 'minute', 'second',
        'possibly_sensitive',
        
        'hashtags', 'user_mentions',
        'original_hashtags', 'retweet_hashtags', 'quote_hashtags',
        'original_user_mentions', 'retweet_user_mentions', 'quote_user_mentions',
        
        'total_in_tweets_cnt',
        'is_original', 'original_favorite_cnt',
                       'original_user_mentions_cnt',
        
        'is_retweet',  'retweet_cnt',
                       'retweet_favorite_cnt', 
                       'retweet_timedelta_sec', 
                       'retweet_from_screen_name', 
                       'retweet_user_mentions_cnt',
                       
        'is_quote',    'quote_cnt',
                       'quote_favorite_cnt',
                       'quote_timedelta_sec', 
                       'quote_from_screen_name',
                       'quote_user_mentions_cnt',
                       
        'is_reply',    'in_reply_cnt',
                       'in_reply_to_screen_name',
    ],
    # User
    'users': [
        'user_id', 'screen_name', 'name', 'verified',
        'location', 'clean_location', 'description', 'is_croatian',
        'followers_count', 'friends_count', 'favourites_count', 
        
        # Outbound User interactions, how much does this User `retweet/reply_to/quote` other Users
        'total_out_tweets_cnt',
        'out_retweets_cnt', 'out_retweets_pct',
        'out_replies_cnt', 'out_replies_pct',
        'out_quotes_cnt', 'out_quotes_pct',
                
        # Inbound User interactions, how much do other Users `retweet/reply_to/quote` this User
        'total_in_tweets_cnt',
        'original_tweets_cnt', 'original_tweets_pct',
        'in_retweets_cnt', 'in_replies_cnt', 'in_quotes_cnt',
        'in_original_favorite_cnt', 'in_retweets_favorite_cnt', 'in_quotes_favorite_cnt',
        
        'hashtags', 'user_mentions',
        'original_hashtags', 'retweet_hashtags', 'quote_hashtags',
        'original_user_mentions', 'retweet_user_mentions', 'quote_user_mentions',
        'original_user_mentions_cnt', 'retweet_user_mentions_cnt', 'quote_user_mentions_cnt',
        
        'retweet_timedelta_sec', 'quote_timedelta_sec',
    ]
}

def preproc():
    print("Initiate preprocessing")
    start_time = dt.datetime.now()
    print("- Users data:", settings.CLEAN_USERS_DIR)
    print("- Tweets data:", settings.CLEAN_TWEETS_DIR)
    print("Analyse data from:", ANALYSIS_MIN_DATE.isoformat())

    clean_users_dfs = utils.read_directory_files(
        directory=settings.CLEAN_USERS_DIR, 
        read_fn=pd.read_csv, 
        dtype=USER_DTYPE,
        parse_dates=['created_at']
    )
    clean_tweets_dfs = utils.read_directory_files(
        directory=settings.CLEAN_TWEETS_DIR, 
        read_fn=pd.read_csv, 
        dtype=TWEET_DTYPE,
        parse_dates=['created_at', 'retweet_created_at']
    )

    users_df = pd.concat(clean_users_dfs)
    users_df = users_df.drop(columns=['created_at'])
    print("Loaded Users data: {:,} records".format(len(users_df)))

    tweets_df = pd.concat(clean_tweets_dfs).drop_duplicates('id')
    tweets_df = tweets_df.loc[tweets_df['created_at'] > ANALYSIS_MIN_DATE].copy()
    print("Loaded Tweet data: {:,} records".format(len(tweets_df)))
    print("- earliest Tweet date:", tweets_df.created_at.min())
    print("- latest Tweet date:", tweets_df.created_at.max())

    print("Evaluating hashtags and user_mentions ...")
    tweets_df['hashtags'] = tweets_df['hashtags'].map(eval)
    tweets_df['user_mentions'] = tweets_df['user_mentions'].map(eval)

    tweets_df['original_hashtags'] = tweets_df['original_hashtags'].map(eval)
    tweets_df['retweet_hashtags'] = tweets_df['retweet_hashtags'].map(eval)
    tweets_df['quote_hashtags'] = tweets_df['quote_hashtags'].map(eval)

    tweets_df['original_user_mentions'] = tweets_df['original_user_mentions'].map(eval)
    tweets_df['retweet_user_mentions'] = tweets_df['retweet_user_mentions'].map(eval)
    tweets_df['quote_user_mentions'] = tweets_df['quote_user_mentions'].map(eval)
    
    tweets_df['original_user_mentions_cnt'] = tweets_df['original_user_mentions'].map(len)
    tweets_df['retweet_user_mentions_cnt'] = tweets_df['retweet_user_mentions'].map(len)
    tweets_df['quote_user_mentions_cnt'] = tweets_df['quote_user_mentions'].map(len)
    print("Evaluation completed")
    
    tweets_df['total_in_tweets_cnt'] = (
        tweets_df['retweet_cnt'] 
        + tweets_df['in_reply_cnt'] 
        + tweets_df['quote_cnt']
    )

    print("Aggregating user metrics ...")
    tweets__user_gdf = tweets_df.groupby('user_id').agg(
        total_out_tweets_cnt=('id', 'size'),
        original_tweets_cnt=('is_original', 'sum'),
        out_retweets_cnt=('is_retweet', 'sum'),
        out_replies_cnt=('is_reply', 'sum'),
        out_quotes_cnt=('is_quote', 'sum'),
        
        in_retweets_cnt=('retweet_cnt', 'sum'),
        in_replies_cnt=('in_reply_cnt', 'sum'),
        in_quotes_cnt=('quote_cnt', 'sum'),
        
        in_original_favorite_cnt=('original_favorite_cnt', 'sum'),
        in_retweets_favorite_cnt=('retweet_favorite_cnt', 'sum'),
        in_quotes_favorite_cnt=('quote_favorite_cnt', 'sum'),
        
        hashtags=('hashtags', 'sum'),
        user_mentions=('user_mentions', 'sum'),
        
        original_hashtags=('original_hashtags', 'sum'),
        retweet_hashtags=('retweet_hashtags', 'sum'),
        quote_hashtags=('quote_hashtags', 'sum'),
        
        original_user_mentions=('original_user_mentions', 'sum'),
        retweet_user_mentions=('retweet_user_mentions', 'sum'),
        quote_user_mentions=('quote_user_mentions', 'sum'),
        
        original_user_mentions_cnt=('original_user_mentions_cnt', 'sum'),
        retweet_user_mentions_cnt=('retweet_user_mentions_cnt', 'sum'),
        quote_user_mentions_cnt=('quote_user_mentions_cnt', 'sum'),
        
        retweet_timedelta_sec=('retweet_timedelta_sec', 'mean'),
        quote_timedelta_sec=('quote_timedelta_sec', 'mean')
    )
    tweets__user_gdf['original_tweets_pct']  = tweets__user_gdf['original_tweets_cnt'] / tweets__user_gdf['total_out_tweets_cnt']
    tweets__user_gdf['out_retweets_pct'] = tweets__user_gdf['out_retweets_cnt'] / tweets__user_gdf['total_out_tweets_cnt']
    tweets__user_gdf['out_replies_pct'] = tweets__user_gdf['out_replies_cnt'] / tweets__user_gdf['total_out_tweets_cnt']
    tweets__user_gdf['out_quotes_pct'] = tweets__user_gdf['out_quotes_cnt'] / tweets__user_gdf['total_out_tweets_cnt']

    users_df = users_df.set_index('user_id')
    
    # Outbound interactions
    users_df['total_out_tweets_cnt']    = tweets__user_gdf['total_out_tweets_cnt'].fillna(0).astype(int)
    users_df['original_tweets_cnt']     = tweets__user_gdf['original_tweets_cnt'].fillna(0).astype(int)
    users_df['original_tweets_pct']     = tweets__user_gdf['original_tweets_pct'].fillna(0)
    users_df['out_retweets_cnt']  = tweets__user_gdf['out_retweets_cnt'].fillna(0).astype(int)
    users_df['out_retweets_pct']  = tweets__user_gdf['out_retweets_pct'].fillna(0)
    users_df['out_replies_cnt']    = tweets__user_gdf['out_replies_cnt'].fillna(0).astype(int)
    users_df['out_replies_pct']    = tweets__user_gdf['out_replies_pct'].fillna(0)
    users_df['out_quotes_cnt']    = tweets__user_gdf['out_quotes_cnt'].fillna(0).astype(int)
    users_df['out_quotes_pct']    = tweets__user_gdf['out_quotes_pct'].fillna(0)

    # Inbound interactions
    users_df['in_retweets_cnt']   = tweets__user_gdf['in_retweets_cnt']
    users_df['in_replies_cnt']     = tweets__user_gdf['in_replies_cnt']
    users_df['in_quotes_cnt']     = tweets__user_gdf['in_quotes_cnt']
    users_df['total_in_tweets_cnt'] = (
        tweets__user_gdf['in_retweets_cnt'] 
        + tweets__user_gdf['in_replies_cnt'] 
        + tweets__user_gdf['in_quotes_cnt']
    )

    users_df['in_original_favorite_cnt'] = tweets__user_gdf['in_original_favorite_cnt'].fillna(0).astype(int)
    users_df['in_retweets_favorite_cnt'] = tweets__user_gdf['in_retweets_favorite_cnt'].fillna(0).astype(int)
    users_df['in_quotes_favorite_cnt']   = tweets__user_gdf['in_quotes_favorite_cnt'].fillna(0).astype(int)

    # Hastags objects
    users_df['hashtags']            = tweets__user_gdf['hashtags']
    users_df['original_hashtags']   = tweets__user_gdf['original_hashtags']
    users_df['retweet_hashtags']    = tweets__user_gdf['retweet_hashtags']
    users_df['quote_hashtags']      = tweets__user_gdf['quote_hashtags']

    # User mentions objects
    users_df['user_mentions']            = tweets__user_gdf['user_mentions']
    users_df['original_user_mentions']   = tweets__user_gdf['original_user_mentions']
    users_df['retweet_user_mentions']    = tweets__user_gdf['retweet_user_mentions']
    users_df['quote_user_mentions']      = tweets__user_gdf['quote_user_mentions']
    
    users_df['original_user_mentions_cnt']   = tweets__user_gdf['original_user_mentions_cnt']
    users_df['retweet_user_mentions_cnt']    = tweets__user_gdf['retweet_user_mentions_cnt']
    users_df['quote_user_mentions_cnt']      = tweets__user_gdf['quote_user_mentions_cnt']

    # Retweet & Quote timedeltas
    users_df['retweet_timedelta_sec']   = tweets__user_gdf['retweet_timedelta_sec']
    users_df['quote_timedelta_sec']     = tweets__user_gdf['quote_timedelta_sec']

    users_view = users_df.reset_index()

    print("Aggregation completed")

    users_view[ANALYSIS_COLUMNS['users']].to_csv(
        'preproc_users_view.csv',
        index=False,
        encoding='utf-8',
        quoting=csv.QUOTE_NONNUMERIC
    )
    print("Exported preproc_users_view.csv")

    tweets_view = tweets_df.merge(
        users_view, 
        on='user_id', 
        suffixes=('', '_user')
    ).rename(columns={'screen_name_user': 'screen_name'})
    tweets_view[ANALYSIS_COLUMNS['tweets'] + ['user_id', 'screen_name', 'followers_count', 'friends_count']].to_csv(
        'preproc_tweets_view.csv',
        index=False,
        encoding='utf-8',
        quoting=csv.QUOTE_NONNUMERIC
    )

    print("Exported preproc_tweets_view.csv")
    end_time = dt.datetime.now()
    print("Time elapsed: {} min".format(end_time-start_time))


if __name__ == '__main__':
    preproc()
