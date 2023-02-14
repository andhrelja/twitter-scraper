from twitter_scraper.clean.users import USER_DTYPE
from twitter_scraper.clean.tweets import TWEET_DTYPE
from twitter_scraper import settings
from twitter_scraper import utils

import datetime as dt
import pandas as pd
import csv


ANALYSIS_MIN_DATE = dt.datetime.fromisoformat('2022-11-01T00:00:00+00:00')
ANALYSIS_COLUMNS = {
    # Tweet
    'tweets': [
        'full_text', 
        'created_at', 'year', 
        'quarter', 'quarter_name',
        'month', 'month_name',
        'week', 'week_name', 
        'day', 'day_name',
        'hour', 'minute', 'second',
        'possibly_sensitive',
        'lemmatized_text',
        
        'hashtags', 'user_mentions', 'all_hashtags',
        'original_hashtags', 'retweet_hashtags', 'quote_hashtags', 
        'original_user_mentions', 'retweet_user_mentions', 'quote_user_mentions',
        
        'total_in_tweets_cnt',
        'is_original', 'original_favorite_cnt',
                       'original_user_mentions_cnt',
        
        'is_retweet',  'in_retweet_cnt',
                       'in_retweet_timedelta_sec',
                       'retweet_favorite_cnt', 
                       'out_retweet_timedelta_sec', 
                       'retweet_from_screen_name', 
                       'retweet_user_mentions_cnt',
                       
        'is_quote',    'in_quote_cnt',
                       'in_quote_timedelta_sec',
                       'quote_favorite_cnt',
                       'out_quote_timedelta_sec', 
                       'quote_from_screen_name',
                       'quote_user_mentions_cnt',
                       
        'is_reply',    'in_reply_cnt',
                       'in_reply_to_screen_name',
    ],
    # User
    'users': [
        'screen_name', 'name', 'verified', 'lemmatized_text',
        'location', 'clean_location', 'description', 'is_croatian',
        'followers_count', 'friends_count', 'favourites_count', 
        
        # Outbound User interactions, how much does this User `retweet/reply_to/quote` other Users
        'total_out_tweets_cnt',
        'original_tweets_cnt',
        'out_retweet_cnt',
        'out_reply_cnt',
        'out_quote_cnt',
                
        # Inbound User interactions, how much do other Users `retweet/reply_to/quote` this User
        'total_in_tweets_cnt',
        'in_retweet_cnt', 'in_reply_cnt', 'in_quote_cnt',
        'in_original_favorite_cnt', 'in_retweet_favorite_cnt', 'in_quote_favorite_cnt',
        
        'hashtags', 'user_mentions', 'all_hashtags',
        'original_hashtags', 'retweet_hashtags', 'quote_hashtags', 
        'original_user_mentions', 'retweet_user_mentions', 'quote_user_mentions',
        'original_user_mentions_cnt', 'retweet_user_mentions_cnt', 'quote_user_mentions_cnt',
        
        'out_retweet_timedelta_sec', 'out_quote_timedelta_sec',
        'in_retweet_timedelta_sec', 'in_quote_timedelta_sec',
    ]
}

def preproc():
    print("Initiate preprocessing")
    start_time = dt.datetime.now()
    print("- Users data:", settings.CLEAN_USERS_DIR)
    print("- Tweets data:", settings.CLEAN_TWEETS_DIR)
    print("- `text` Tweets data:", settings.TEXT_DIR)
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
    text_dfs = utils.read_directory_files(
        directory=settings.TEXT_DIR,
        read_fn=pd.read_csv,
        parse_dates=['created_at']
    )

    # Users
    users_df = pd.concat(clean_users_dfs)
    users_view = users_df.drop(columns=['created_at']).set_index('user_id')
    print("Loaded Users data: {:,} records".format(len(users_view)))

    # Tweets
    tweets_df = pd.concat(clean_tweets_dfs).drop_duplicates('id')
    tweets_df = tweets_df.loc[tweets_df['created_at'] >= ANALYSIS_MIN_DATE].set_index('id')
    print("Loaded Tweet data: {:,} records".format(len(tweets_df)))
    print("- earliest Tweet date:", tweets_df.created_at.min())
    print("- latest Tweet date:", tweets_df.created_at.max())

    # `text` Tweets
    text_df = pd.concat(text_dfs).drop_duplicates('id')
    text_df = text_df.dropna(subset=['lemmatized'])
    text_df = text_df.loc[text_df['created_at'] >= ANALYSIS_MIN_DATE]
    print("Loaded `text` Tweet data: {:,} records".format(len(text_df)))
    print("- earliest `text` Tweet date:", text_df.created_at.min())
    print("- latest `text` Tweet date:", text_df.created_at.max())
    text_df = text_df[['id', 'lemmatized']].set_index('id')
    tweets_df = tweets_df.join(text_df, how='left')
    tweets_df['lemmatized_text'] = tweets_df['lemmatized'].fillna('[]')

    # Start evaluation
    
    print("Evaluating hashtags, user_mentions and `text`...")
    tweets_df['lemmatized_text'] = tweets_df['lemmatized_text'].map(eval)    
    tweets_df['hashtags'] = tweets_df['hashtags'].map(eval)
    tweets_df['user_mentions'] = tweets_df['user_mentions'].map(eval)

    tweets_df['original_hashtags'] = tweets_df['original_hashtags'].map(eval)
    tweets_df['retweet_hashtags'] = tweets_df['retweet_hashtags'].map(eval)
    tweets_df['quote_hashtags'] = tweets_df['quote_hashtags'].map(eval)
    tweets_df['all_hashtags'] = (
        tweets_df['original_hashtags'] 
        + tweets_df['retweet_hashtags'] 
        + tweets_df['quote_hashtags']
    )

    tweets_df['original_user_mentions'] = tweets_df['original_user_mentions'].map(eval)
    tweets_df['retweet_user_mentions'] = tweets_df['retweet_user_mentions'].map(eval)
    tweets_df['quote_user_mentions'] = tweets_df['quote_user_mentions'].map(eval)
    
    tweets_df['original_user_mentions_cnt'] = tweets_df['original_user_mentions'].map(len)
    tweets_df['retweet_user_mentions_cnt'] = tweets_df['retweet_user_mentions'].map(len)
    tweets_df['quote_user_mentions_cnt'] = tweets_df['quote_user_mentions'].map(len)
    print("Evaluation completed")
    
    tweets_df['total_in_tweets_cnt'] = (
        tweets_df['in_retweet_cnt'] 
        + tweets_df['in_reply_cnt'] 
        + tweets_df['in_quote_cnt']
    )

    print("Aggregating user metrics ...")
    tweets__user_gdf = tweets_df.groupby('user_id').agg(
        total_out_tweets_cnt=('user_id', 'count'),
        original_tweets_cnt=('is_original', 'sum'),
        out_retweet_cnt=('is_retweet', 'sum'),
        out_reply_cnt=('is_reply', 'sum'),
        out_quote_cnt=('is_quote', 'sum'),
        
        in_retweet_cnt=('in_retweet_cnt', 'sum'),
        in_reply_cnt=('in_reply_cnt', 'sum'),
        in_quote_cnt=('in_quote_cnt', 'sum'),
        
        in_original_favorite_cnt=('original_favorite_cnt', 'sum'),
        in_retweet_favorite_cnt=('retweet_favorite_cnt', 'sum'),
        in_quote_favorite_cnt=('quote_favorite_cnt', 'sum'),
        
        hashtags=('hashtags', 'sum'),
        user_mentions=('user_mentions', 'sum'),
        lemmatized_text=('lemmatized_text', 'sum'),
        
        original_hashtags=('original_hashtags', 'sum'),
        retweet_hashtags=('retweet_hashtags', 'sum'),
        quote_hashtags=('quote_hashtags', 'sum'),
        
        original_user_mentions=('original_user_mentions', 'sum'),
        retweet_user_mentions=('retweet_user_mentions', 'sum'),
        quote_user_mentions=('quote_user_mentions', 'sum'),
        
        original_user_mentions_cnt=('original_user_mentions_cnt', 'sum'),
        retweet_user_mentions_cnt=('retweet_user_mentions_cnt', 'sum'),
        quote_user_mentions_cnt=('quote_user_mentions_cnt', 'sum'),
        
        out_retweet_timedelta_sec=('retweet_timedelta_sec', 'mean'),
        out_quote_timedelta_sec=('quote_timedelta_sec', 'mean'),
        in_retweet_timedelta_sec=('in_retweet_timedelta_sec', 'mean'),
        in_quote_timedelta_sec=('in_quote_timedelta_sec', 'mean'),
    )
    # Outbound interactions
    users_view['total_out_tweets_cnt']     = tweets__user_gdf['total_out_tweets_cnt'].fillna(0).astype(int)
    users_view['original_tweets_cnt']      = tweets__user_gdf['original_tweets_cnt'].fillna(0).astype(int)
    users_view['out_retweet_cnt']  = tweets__user_gdf['out_retweet_cnt'].fillna(0).astype(int)
    users_view['out_reply_cnt']    = tweets__user_gdf['out_reply_cnt'].fillna(0).astype(int)
    users_view['out_quote_cnt']    = tweets__user_gdf['out_quote_cnt'].fillna(0).astype(int)

    # Inbound interactions
    users_view['in_retweet_cnt']   = tweets__user_gdf['in_retweet_cnt']
    users_view['in_reply_cnt']     = tweets__user_gdf['in_reply_cnt']
    users_view['in_quote_cnt']     = tweets__user_gdf['in_quote_cnt']
    users_view['total_in_tweets_cnt'] = (
        tweets__user_gdf['in_retweet_cnt'] 
        + tweets__user_gdf['in_reply_cnt'] 
        + tweets__user_gdf['in_quote_cnt']
    )

    users_view['in_original_favorite_cnt']    = tweets__user_gdf['in_original_favorite_cnt'].fillna(0).astype(int)
    users_view['in_retweet_favorite_cnt']     = tweets__user_gdf['in_retweet_favorite_cnt'].fillna(0).astype(int)
    users_view['in_quote_favorite_cnt']       = tweets__user_gdf['in_quote_favorite_cnt'].fillna(0).astype(int)

    # Hastags objects
    users_view['hashtags']            = tweets__user_gdf['hashtags']
    users_view['original_hashtags']   = tweets__user_gdf['original_hashtags']
    users_view['retweet_hashtags']    = tweets__user_gdf['retweet_hashtags']
    users_view['quote_hashtags']      = tweets__user_gdf['quote_hashtags']
    users_view['all_hashtags'] = (
        users_view['original_hashtags'] 
        + users_view['retweet_hashtags'] 
        + users_view['quote_hashtags']
    )

    # User mentions objects
    users_view['user_mentions']              = tweets__user_gdf['user_mentions']
    users_view['original_user_mentions']     = tweets__user_gdf['original_user_mentions']
    users_view['retweet_user_mentions']      = tweets__user_gdf['retweet_user_mentions']
    users_view['quote_user_mentions']        = tweets__user_gdf['quote_user_mentions']
    
    users_view['original_user_mentions_cnt'] = tweets__user_gdf['original_user_mentions_cnt']
    users_view['retweet_user_mentions_cnt']  = tweets__user_gdf['retweet_user_mentions_cnt']
    users_view['quote_user_mentions_cnt']    = tweets__user_gdf['quote_user_mentions_cnt']
    
    # Lemmatized text
    users_view['lemmatized_text']            = tweets__user_gdf['lemmatized_text']
    
    # Retweet & Quote timedeltas
    users_view['out_retweet_timedelta_sec']  = tweets__user_gdf['out_retweet_timedelta_sec']
    users_view['out_quote_timedelta_sec']    = tweets__user_gdf['out_quote_timedelta_sec']
    users_view['in_retweet_timedelta_sec']   = tweets__user_gdf['in_retweet_timedelta_sec']
    users_view['in_quote_timedelta_sec']     = tweets__user_gdf['in_quote_timedelta_sec']

    tweets_view = tweets_df.merge(
        users_view.rename(columns={'screen_name_user': 'screen_name'}), 
        on='user_id', 
        suffixes=('', '_user')
    )

    print("Aggregation completed")
    
    users_view[
        ANALYSIS_COLUMNS['users']
    ].to_csv(
        'preproc_users_view.csv',
        index=True,
        encoding='utf-8',
        quoting=csv.QUOTE_NONNUMERIC
    )
    print("Exported preproc_users_view.csv")

    tweets_view[
        ANALYSIS_COLUMNS['tweets'] + ['user_id', 'screen_name', 'followers_count', 'friends_count']
    ].to_csv(
        'preproc_tweets_view.csv',
        index=True,
        encoding='utf-8',
        quoting=csv.QUOTE_NONNUMERIC
    )
    print("Exported preproc_tweets_view.csv")
    
    end_time = dt.datetime.now()
    print("Time elapsed: {} min".format(end_time-start_time))


if __name__ == '__main__':
    preproc()
