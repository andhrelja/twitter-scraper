# %%
import os
import json
import pytz
import pandas as pd
import datetime as dt

from twitter_scraper import settings


MIN_DATE = dt.datetime(2021, 8, 1, 0, 0, 0, 0, pytz.UTC)
MAX_DATE = dt.datetime(2022, 1, 31, 0, 0, 0, 0, pytz.UTC)

CLEAN_TWEET = lambda x: {
    'id':               str(x.get('id')),
    'user_id':          str(x.get('user_id')),
    'full_text':        x.get('full_text'),
    'created_at':       x.get('created_at'),
    'hashtags':         x.get('hashtags'),
    'user_mentions':    x.get('user_mentions'),
    'retweet_user':     x.get('retweet_user'),
    'retweet_count':    x.get('retweet_count'),
	# 'in_reply_to_status_id':      x.get('in_reply_to_status_id'),
	# 'in_reply_to_status_id_str':  x.get('in_reply_to_status_id_str'),
	# 'in_reply_to_user_id':        x.get('in_reply_to_user_id'),
	# 'in_reply_to_user_id_str':    x.get('in_reply_to_user_id_str'),
	# 'in_reply_to_screen_name':    x.get('in_reply_to_screen_name'),
	'geo':              x.get('geo'),
	'coordinates':      x.get('coordinates'),
	# 'place':          x.get('place'),
	# 'contributors':   x.get('contributors'),
	# 'is_quote_status': x.get('is_quote_status'),
	# 'favorite_count': x.get('favorite_count'),
	# 'favorited':      x.get('favorited'),
	# 'retweeted':      x.get('retweeted'),
	# 'possibly_sensitive': x.get('possibly_sensitive'),
	# 'lang': x.get('lang')
}


def get_tweets_df():
    if not os.path.exists(settings.TWEETS_CSV):
        print("Creating df from output files")
        data = []
        for fn in os.listdir(settings.USER_TWEETS_DIR):
            with open(os.path.join(settings.USER_TWEETS_DIR, fn), 'r', encoding='utf-8') as f:
                content = json.load(f)
            data += [CLEAN_TWEET(item) for item in content]

        tweets_df = pd.DataFrame(data)
        tweets_df['created_at'] = pd.to_datetime(tweets_df['created_at'], format='%a %b %d %H:%M:%S %z %Y') # 30s
        tweets_df['week']  = tweets_df['created_at'].dt.strftime('%Y-%W')
        tweets_df['month'] = tweets_df['created_at'].dt.strftime('%Y-%m')
    else:
        print("Reading CSV")
        tweets_df = pd.read_csv(settings.TWEETS_CSV)
        tweets_df['created_at'] = pd.to_datetime(tweets_df['created_at'], format='%Y-%m-%d %H:%M:%S%z') # 30s

    tweets_df = tweets_df[
        (tweets_df['created_at'] > MIN_DATE)
        & (tweets_df['created_at'] < MAX_DATE)
    ]

    tweets_df['is_covid'] = tweets_df['full_text'].fillna('').transform(lambda x: any((tag in x.lower()
                                                        or tag.replace(' ', '') in x.replace(' ', ''))
                                                        for tag in settings.KEYWORDS['is_covid']))
    print("Done\n")
    return tweets_df

# %%

def get_users_df(tweets_df):
    users_df = tweets_df.groupby('user_id').agg(total_tweets=('user_id', 'size'))
    users_df['covid_tweets']    = tweets_df[tweets_df['is_covid'] == True].groupby('user_id').size()
    users_df['is_covid']        = users_df['covid_tweets'].transform(lambda x: x > 0)
    users_df['covid_tweets']    = users_df['covid_tweets'].fillna(0)
    users_df['covid_pct']       = users_df['covid_tweets'] / users_df['total_tweets']
    users_df                    = users_df.reset_index(drop=False)
    users_df['user_id']         = users_df['user_id'].astype(str)
    return users_df


# %%
def tweets():
    print("{} - Cleaning tweets ...".format(dt.datetime.now()))
    
    nodes_graph_dir, _ = os.path.split(settings.NODES_CSV)
    tweets_csv_dir, _ = os.path.split(settings.TWEETS_CSV)
    if not os.path.exists(nodes_graph_dir):
        os.mkdir(nodes_graph_dir)
    if not os.path.exists(tweets_csv_dir):
        os.mkdir(tweets_csv_dir)
    
    tweets_df = get_tweets_df()
    tweets_df.to_csv(settings.TWEETS_CSV, encoding='utf-8', index=False)
    users_df = get_users_df(tweets_df)
    users_df.to_csv(settings.NODES_CSV, encoding='utf-8', index=False)
    
# %%
