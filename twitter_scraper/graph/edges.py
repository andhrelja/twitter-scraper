# %%
import os
import time
import pandas as pd
import datetime as dt
from tqdm import tqdm

from twitter_scraper import utils
from twitter_scraper.utils import fileio
from twitter_scraper import settings
from twitter_scraper.clean.tweets import TWEET_DTYPE
from twitter_scraper.graph.nodes import NODE_DTYPE

logger = utils.get_logger(__file__)

EDGE_DTYPE = {
    'source': 'int64',
    'target': 'int64',
    'timestamp': 'int64'
}

# %%
def get_user_followers_edges_df(nodes_df):
    not_found = []
    users_friends = {}

    for user_id_str in tqdm(nodes_df.user_id_str.unique()):
        user_path = os.path.join(settings.USER_IDS_DIR, '{}.json'.format(user_id_str))
        if os.path.exists(user_path):
            user_ids_content = fileio.read_content(user_path, 'json')
            users_friends[user_id_str] = user_ids_content[user_id_str]['friends']
        else:
            not_found.append(user_id_str)

    if not users_friends:
        return pd.DataFrame([]), 0, 0

    users_data = []
    for user_id_str, friends_ids in users_friends.items():
        for friend_id in friends_ids:
            users_data.append((friend_id, int(user_id_str)))

    total_users = len(nodes_df.user_id_str.unique())
    found = total_users - len(not_found)
    
    edges_df = pd.DataFrame(users_data, columns=['source', 'target'])
    edges_df = edges_df[(edges_df['source'].isin(nodes_df.user_id.unique())) & (edges_df['target'].isin(nodes_df.user_id.unique()))]
    # new_edges_df = new_edges_df.set_index(['source', 'target'])
    # if os.path.isfile(settings.EDGES_FOLLOWERS_CSV):
    #     existing_edges_df = pd.read_csv(settings.EDGES_FOLLOWERS_CSV, index_col=['source', 'target'])
    #     edges_df = existing_edges_df.join(new_edges_df, how='right')
    #     edges_df['timestamp'] = edges_df['timestamp'].fillna(int(dt.datetime.now(dt.timezone.utc).timestamp()))
    # else:
    #     edges_df = new_edges_df
    #     edges_df['timestamp'] = int(dt.datetime.now(dt.timezone.utc).timestamp())
    # edges_df = edges_df.reset_index(drop=False)
    edges_df['timestamp'] = int(dt.datetime.now(dt.timezone.utc).timestamp())
    return edges_df[EDGE_DTYPE.keys()].astype(EDGE_DTYPE), total_users, found


def get_user_mentions_edges_df(nodes_df, tweets_df):
    nodes_df = nodes_df.set_index('user_id')
    tweets_df['user_mentions'] = tweets_df['user_mentions'].apply(eval)
    nodes_df['user_mentions'] = tweets_df[['user_id', 'user_mentions']].groupby('user_id').agg(user_mentions=('user_mentions', sum))
    nodes_df = nodes_df.reset_index()
    edges_df = nodes_df[['user_id', 'user_mentions']].rename(columns={'user_id': 'source', 'user_mentions': 'target'})
    edges_df = edges_df.explode('target').reset_index(drop=True)
    edges_df = edges_df.loc[(edges_df['target'].isin(nodes_df['user_id'])) & (edges_df['source'] != edges_df['target'])]
    
    total_users = len(nodes_df.user_id.unique())
    not_found = total_users - len(edges_df.source.unique())
    found = total_users - not_found
    
    # Create self loops for users who don't have a `user mention`
    edges_df.loc[edges_df['target'].isna(), 'target'] = edges_df['source']
    edges_df['timestamp'] = dt.datetime.now(dt.timezone.utc).timestamp()
    return edges_df[EDGE_DTYPE.keys()].astype(EDGE_DTYPE), total_users, found


def get_user_retweets_edges_df(nodes_df, tweets_df):
    edge_dtype = dict(id='int64', **EDGE_DTYPE)
    edges_df = tweets_df[['id', 'user_id', 'retweet_from_user_id']].rename(columns={'id': 'id', 'user_id': 'target', 'retweet_from_user_id': 'source'})
    edges_df = edges_df.dropna()
    edges_df = edges_df.loc[edges_df['source'].isin(nodes_df['user_id'])]
    
    total_users = len(nodes_df.user_id.unique())
    not_found = total_users - len(edges_df.source.unique())
    found = total_users - not_found
    
    edges_df['timestamp'] = dt.datetime.now(dt.timezone.utc).timestamp()
    return edges_df[edge_dtype.keys()].astype(edge_dtype), total_users, found


# %%
def user_followers_edges():
    start_time = time.time()
    
    utils.mkdir(os.path.dirname(settings.TWEETS_CSV))
    NODES_DF = pd.read_csv(settings.NODES_CSV, dtype=NODE_DTYPE)

    logger.info("START - Creating User Followers Edges, this may take a while")
    
    edges_df, total_users, found = get_user_followers_edges_df(NODES_DF)
    if edges_df.empty:
        logger.warning("No Edges were found, inspect baseline-user-ids.json:\n"
            "\t- found {}/{} nodes\n"
            "\t- found edges for {}/{} nodes".format(
                found, total_users,
                0, found
            )
        )
    else:
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
    logger.info("END - Done creating User Followers Edges")
    logger.info("Time elapsed: {} min".format(round((end_time - start_time)/60, 2)))


def user_mentions_edges():
    start_time = time.time()
    
    utils.mkdir(os.path.dirname(settings.TWEETS_CSV))
    nodes_df = pd.read_csv(settings.NODES_CSV, dtype=NODE_DTYPE)

    logger.info("START - Creating User Mentions Edges, this may take a while")

    tweets_df = pd.read_csv(settings.TWEETS_CSV)
    tweets_df = tweets_df.astype(TWEET_DTYPE)

    edges_df, total_users, found = get_user_mentions_edges_df(nodes_df, tweets_df)
    if edges_df.empty:
        logger.warning("No Edges were found, inspect baseline-user-ids.json:\n"
            "\t- found {}/{} nodes\n"
            "\t- found edges for {}/{} nodes".format(
                found, total_users,
                0, found
            )
        )
    else:
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
    logger.info("END - Done creating User Mentions Edges")
    logger.info("Time elapsed: {} min".format(round((end_time - start_time)/60, 2)))


def user_retweets_edges():
    start_time = time.time()
    
    utils.mkdir(os.path.dirname(settings.TWEETS_CSV))
    nodes_df = pd.read_csv(settings.NODES_CSV, dtype=NODE_DTYPE)

    logger.info("START - Creating User Retweets Edges, this may take a while")

    tweets_df = pd.read_csv(settings.TWEETS_CSV)
    tweets_df = tweets_df.astype(TWEET_DTYPE)

    edges_df, total_users, found = get_user_retweets_edges_df(nodes_df, tweets_df)
    if edges_df.empty:
        logger.warning("No Edges were found, inspect baseline-user-ids.json:\n"
            "\t- found {}/{} nodes\n"
            "\t- found edges for {}/{} nodes".format(
                found, total_users,
                0, found
            )
        )
    else:
        edges_df.to_csv(settings.EDGES_RETWEETS_CSV, index=False)
        logger.info("Wrote Edges df: {}\n"
            "\t- found {}/{} nodes\n"
            "\t- found edges for {}/{} nodes".format(
                settings.EDGES_RETWEETS_CSV,
                found, total_users,
                len(edges_df.source.unique()), found
            )
        )

    end_time = time.time()
    logger.info("END - Done creating User Retweets Edges")
    logger.info("Time elapsed: {} min".format(round((end_time - start_time)/60, 2)))


def edges(user_followers=True, user_mentions=True, user_retweets=True):
    if user_followers:
        user_followers_edges()
    if user_mentions:
        user_mentions_edges()
    if user_retweets:
        user_retweets_edges()

# %%
if __name__ == '__main__':
    edges(user_followers=True, user_mentions=True, user_retweets=True)
