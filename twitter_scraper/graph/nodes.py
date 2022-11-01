# %%
import os
import csv
import time
import pandas as pd

from twitter_scraper import utils
from twitter_scraper import settings
from twitter_scraper.clean.tweets import TWEET_DTYPE
from twitter_scraper.clean.users import USER_DTYPE

logger = utils.get_logger(__file__)

NODE_DTYPE = {
    'user_id':          'int64',
    'user_id_str':      'string',
    'screen_name':      'string',
    'followers_count':  'int',
    'friends_count':    'int',
    'listed_count':     'int',
    'favourites_count': 'int',
    'statuses_count':   'int',
    
    ### Custom columns
    'total_tweets':     'int',
    'covid_tweets':     'int',
    'covid_pct':        'float',
    'is_covid':         'bool',
    # 'in_dc':            'float',
    # 'out_dc':           'float',
    # 'in_d':             'float',
    # 'out_d':            'float',
}

# %%
def get_nodes_df(tweets_df, user_df):
    nodes_df = tweets_df.groupby('user_id_str').agg(total_tweets=('user_id_str', 'size')).join(user_df.set_index('user_id_str'), how='inner')
    nodes_df['covid_tweets']    = tweets_df[tweets_df['is_covid'] == True].groupby('user_id_str').size()
    nodes_df['is_covid']        = nodes_df['covid_tweets'].transform(lambda x: x > 0)
    nodes_df['covid_tweets']    = nodes_df['covid_tweets'].fillna(0).astype(int)
    nodes_df['covid_pct']       = nodes_df['covid_tweets'] / nodes_df['total_tweets']
    nodes_df                    = nodes_df.reset_index(drop=False)
    return nodes_df[NODE_DTYPE.keys()].astype(NODE_DTYPE)

# %%
def nodes():
    start_time = time.time()
    
    utils.mkdir(os.path.dirname(settings.NODES_CSV))
    
    logger.info("START - Creating Graph data")
    user_df = pd.read_csv(settings.USERS_CSV, dtype=USER_DTYPE)
    tweets_df = pd.read_csv(settings.TWEETS_CSV, dtype=TWEET_DTYPE)

    logger.info("Creating Nodes df, this may take a while")
    nodes_df = get_nodes_df(tweets_df, user_df)
    nodes_df.to_csv(settings.NODES_CSV, index=False, quoting=csv.QUOTE_NONNUMERIC)
    logger.info("Wrote Nodes df")
    logger.info("Graph nodes saved: {}".format(settings.NODES_CSV))
    
    end_time = time.time()
    logger.info("END - Done creating Graph data")
    logger.info("Time elapsed: {} min".format(round((end_time - start_time)/60, 2)))


if __name__ == '__main__':
    nodes()
