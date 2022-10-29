# %%
import os
import time
import pandas as pd
# import datetime as dt
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
    # 'timestamp': 'int64'
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
    # edges_df['timestamp'] = int(dt.datetime.now(dt.timezone.utc).timestamp())
    return edges_df[EDGE_DTYPE.keys()].astype(EDGE_DTYPE), total_users, found


def get_user_mentions_edges_df(nodes_df, tweets_df):
    nodes_df = nodes_df.set_index('user_id')
    tweets_df['user_mentions'] = tweets_df['user_mentions'].apply(eval)
    nodes_df['user_mentions'] = tweets_df[[
        'user_id', 
        'user_mentions'
    ]].groupby('user_id').agg(user_mentions=('user_mentions', sum))
    nodes_df = nodes_df.reset_index()
    edges_df = nodes_df[['user_id', 'user_mentions']].rename(columns={'user_id': 'source', 'user_mentions': 'target'})
    edges_df = edges_df.explode('target').reset_index(drop=True)
    edges_df = edges_df.loc[(edges_df['target'].isin(nodes_df['user_id'])) & (edges_df['source'] != edges_df['target'])]
    
    total_users = len(nodes_df.user_id.unique())
    not_found = total_users - len(edges_df.source.unique())
    found = total_users - not_found
    
    # Create self loops for users who don't have a `user mention`
    edges_df.loc[edges_df['target'].isna(), 'target'] = edges_df['source']
    # edges_df['timestamp'] = dt.datetime.now(dt.timezone.utc).timestamp()
    return edges_df[EDGE_DTYPE.keys()].astype(EDGE_DTYPE), total_users, found


def get_user_retweets_edges_df(nodes_df, tweets_df):
    apis = utils.api.get_api_connections()
    def get_og_full_text(tweet_id, conn_name='Carlos'):
        og_full_text_idx = tweets_df[['id', 'full_text']].set_index('id').to_dict()['full_text']
        api = apis[conn_name]
        if tweet_id in og_full_text_idx:
            return og_full_text_idx[tweet_id]
        tweet, _ = utils.api.get_twitter_endpoint(conn_name, api, 'get_status', user_id=None, id=tweet_id)
        if tweet:
            return tweet.text
        return None
        
    # Has a custom edge_dtype
    edge_dtype = dict(**EDGE_DTYPE,
        rt_tweet_id='int64',
        full_text='string',
        og_tweet_id='int64',
        rt_time_elapsed_sec='float64'
    )
    
    edges_df = tweets_df[[
        'id',
        'retweet_from_tweet_id', 
        'user_id', 
        'retweet_from_user_id',
        'created_at',
        'full_text'
    ]].rename(columns={
        'id': 'rt_tweet_id',
        'retweet_from_tweet_id': 'og_tweet_id', 
        'user_id': 'target', 
        'retweet_from_user_id': 'source',
        'created_at': 'rt_created_at'
    })
    edges_df = edges_df.dropna()
    edges_df = edges_df.loc[edges_df['source'].isin(nodes_df['user_id'])]
    edges_df = edges_df.merge(tweets_df[['id', 'created_at']].rename(columns={
        'created_at': 'og_created_at'
    }), left_on='og_tweet_id', right_on='id', how='left').drop('id', axis=1)
    # edges_df['_full_text'] = edges_df['og_tweet_id'].transform(get_og_full_text)
    # edges_df['full_text'] = edges_df['_full_text'] or edges_df['full_text']
    edges_df['rt_created_at'] = pd.to_datetime(edges_df['rt_created_at'])
    edges_df['og_created_at'] = pd.to_datetime(edges_df['og_created_at'])
    edges_df['rt_time_elapsed_sec'] = (edges_df['rt_created_at'] - edges_df['og_created_at']).map(lambda x: x.total_seconds())
    total_users = len(nodes_df.user_id.unique())
    not_found = total_users - len(edges_df.source.unique())
    found = total_users - not_found
    
    # edges_df['timestamp'] = dt.datetime.now(dt.timezone.utc).timestamp()
    return edges_df[edge_dtype.keys()].astype(edge_dtype), total_users, found


# %%
def user_followers_edges():
    start_time = time.time()
    
    utils.mkdir(os.path.dirname(settings.TWEETS_CSV))
    NODES_DF = pd.read_csv(settings.NODES_CSV, dtype=NODE_DTYPE)

    logger.info("START - Creating User Followers Edges, this may take a while")
    
    edges_df, nodes_len, found_followers = get_user_followers_edges_df(NODES_DF)
    if edges_df.empty:
        message = "No Edges were found, inspect baseline-user-ids.json:\n"
        len_followers_source = 0
        log = logger.warning
    else:
        message = "Wrote Edges df: {}\n".format(settings.EDGES_FOLLOWERS_CSV)
        len_followers_source = len(edges_df.source.unique())
        log = logger.info
        edges_df.to_csv(settings.EDGES_FOLLOWERS_CSV, index=False)
        
    len_followers = len(edges_df)
    log(message + \
        "\t- found {}/{} nodes\n"
        "\t- found edges for {}/{} nodes".format(
            found_followers, nodes_len, 
            len_followers_source, found_followers
        )
    )
    
    fileio.write_content(
        path=os.path.join(settings.LOGS_DIR, '{}.json'.format(settings.folder_name)),
        content={
            'nodes_len': nodes_len,
            'found_followers': found_followers,
            'len_followers_source': len_followers_source,
            'len_followers': len_followers
        },
        file_type='json'
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

    edges_df, nodes_len, found_mentions = get_user_mentions_edges_df(nodes_df, tweets_df)
    if edges_df.empty:
        message = "No Edges were found, inspect baseline-user-ids.json:\n"
        len_mentions_source = 0
        log = logger.warning
    else:
        message = "Wrote Edges df: {}\n".format(settings.EDGES_MENTIONS_CSV)
        len_mentions_source = len(edges_df.source.unique())
        log = logger.info
        edges_df.to_csv(settings.EDGES_MENTIONS_CSV, index=False)
        
    len_mentions = len(edges_df)
    log(message + \
        "\t- found {}/{} nodes\n"
        "\t- found edges for {}/{} nodes".format(
            found_mentions, nodes_len, 
            len_mentions_source, found_mentions
        )
    )
    
    fileio.write_content(
        path=os.path.join(settings.LOGS_DIR, '{}.json'.format(settings.folder_name)),
        content={
            'nodes_len': nodes_len,
            'found_mentions': found_mentions,
            'len_mentions_source': len_mentions_source,
            'len_mentions': len_mentions
        },
        file_type='json'
    )
    
    end_time = time.time()
    logger.info("END - Done creating User Mentions Edges")
    logger.info("Time elapsed: {} min".format(round((end_time - start_time)/60, 2)))


def user_retweets_edges():
    start_time = time.time()
    
    utils.mkdir(os.path.dirname(settings.TWEETS_CSV))
    nodes_df = pd.read_csv(settings.NODES_CSV, dtype=NODE_DTYPE)

    logger.info("START - Creating User Retweets Edges, this may take a while")

    tweets_df = pd.read_csv(settings.TWEETS_CSV, dtype=TWEET_DTYPE)
    # tweets_df = tweets_df.astype(TWEET_DTYPE)

    edges_df, nodes_len, found_retweets = get_user_retweets_edges_df(nodes_df, tweets_df)
    if edges_df.empty:
        message = "No Edges were found, inspect baseline-user-ids.json:\n"
        len_retweets_source = 0
        log = logger.warning
    else:
        message = "Wrote Edges df: {}\n".format(settings.EDGES_RETWEETS_CSV)
        len_retweets_source = len(edges_df.source.unique())
        log = logger.info
        edges_df.to_csv(settings.EDGES_RETWEETS_CSV, index=False)
        
    len_retweets = len(edges_df)
    log(message + \
        "\t- found {}/{} nodes\n"
        "\t- found edges for {}/{} nodes".format(
            found_retweets, nodes_len, 
            len_retweets_source, found_retweets
        )
    )
    
    fileio.write_content(
        path=os.path.join(settings.LOGS_DIR, '{}.json'.format(settings.folder_name)),
        content={
            'nodes_len': nodes_len,
            'found_retweets': found_retweets,
            'len_retweets_source': len_retweets_source,
            'len_retweets': len_retweets
        },
        file_type='json'
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
    edges(user_followers=False, user_mentions=False, user_retweets=True)
