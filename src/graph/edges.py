# %%
import os
import time
import pandas as pd
from tqdm import tqdm

import utils
from utils import fileio
from twitter_scraper import settings
from clean.tweets import TWEET_DTYPE
from graph.nodes import NODE_DTYPE

logger = utils.get_logger(__file__)

EDGE_DTYPE = {
    'source': 'int64',
    'target': 'int64',
}

# %%
def get_user_followers_edges_df(nodes_df):
    not_found = []
    users_data = []
    
    for user_id_str in tqdm(nodes_df.user_id_str.unique()):
        user_path = os.path.join(settings.USER_IDS_DIR, '{}.json'.format(user_id_str))
        if os.path.exists(user_path):
            user = fileio.read_content(user_path, 'json')
            for follower in user[user_id_str].get('followers', []):
                if str(follower) in nodes_df.user_id_str.unique():
                    users_data.append({
                        'source': int(follower),
                        'target': int(user_id_str)
                    })
        else:
            not_found.append(user_id_str)
    
    total_users = len(nodes_df.user_id_str.unique())
    found = total_users - len(not_found)
    
    edges_df = pd.DataFrame(users_data, columns=['source', 'target'])
    return edges_df[EDGE_DTYPE.keys()].astype(EDGE_DTYPE), total_users, found


def get_user_mentions_edges_df(nodes_df, tweets_df):
    nodes_df = nodes_df.set_index('user_id_str')
    tweets_df['user_mentions'] = tweets_df['user_mentions'].apply(eval)
    nodes_df['user_mentions'] = tweets_df[['user_id_str', 'user_mentions']].groupby('user_id').sum()
    nodes_df = nodes_df.reset_index()
    edges_df = nodes_df[['user_id_str', 'user_mentions']].rename(columns={'user_id_str': 'source', 'user_mentions': 'target'})
    edges_df = edges_df.explode('target').reset_index(drop=True)
    
    total_users = len(nodes_df)
    not_found = len(nodes_df[nodes_df['user_mentions'].isna()])
    found = total_users - not_found
    
    # Create self loops for users who don't have a `user mention`
    edges_df.loc[edges_df['target'].isna(), 'target'] = edges_df['source']
    return edges_df[EDGE_DTYPE.keys()].astype(EDGE_DTYPE), total_users, found


# %%
def user_followers_edges():
    start_time = time.time()
    
    utils.mkdir(os.path.dirname(settings.TWEETS_CSV))
    NODES_DF = pd.read_csv(settings.NODES_CSV, dtype=NODE_DTYPE)

    logger.info("START - Creating User Followers Edges")
    logger.info("Creating Edges df, this may take a while")

    
    edges_df, total_users, found = get_user_followers_edges_df(NODES_DF)
    edges_df.to_csv(settings.EDGES_FOLLOWERS_CSV, index=False)
    logger.info("Wrote Edges df: {}\n"
        "\t- found {}/{} nodes\n"
        "\t- found edges for {}/{} nodes".format(
            settings.EDGES_FOLLOWERS_CSV, 
            found, total_users, 
            len(edges_df.source.unique()), found
        )
    )

    end_time = time.time()
    logger.info("END - Done creating Graph data")
    logger.info("Time elapsed: {} min".format(round((end_time - start_time)/60, 2)))


def user_mentions_edges():
    start_time = time.time()
    
    utils.mkdir(os.path.dirname(settings.TWEETS_CSV))
    NODES_DF = pd.read_csv(settings.NODES_CSV, dtype=NODE_DTYPE)

    logger.info("START - Creating User Mentions Edges")
    logger.info("Creating Edges df, this may take a while")

    tweets_df = pd.read_csv(settings.TWEETS_CSV)
    tweets_df = tweets_df.astype(TWEET_DTYPE)

    edges_df, total_users, found = get_user_mentions_edges_df(NODES_DF, tweets_df)
    edges_df.to_csv(settings.EDGES_MENTIONS_CSV, index=False)
    logger.info("Wrote Edges df: {}\n"
        "\t- found {}/{} nodes\n"
        "\t- found edges for {}/{} nodes".format(
            settings.EDGES_MENTIONS_CSV,
            found, total_users,
            len(edges_df.source.unique()), found
        )
    )

    end_time = time.time()
    logger.info("END - Done creating Graph data")
    logger.info("Time elapsed: {} min".format(round((end_time - start_time)/60, 2)))


def edges(user_followers=True, user_mentions=True):
    if user_followers:
        user_followers_edges()
    if user_mentions:
        user_mentions_edges()

# %%
if __name__ == '__main__':
    #user_followers_edges()
    user_mentions_edges()