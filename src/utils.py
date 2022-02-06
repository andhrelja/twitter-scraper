import os
import time
import tweepy
import requests.exceptions
from tqdm import tqdm

import fileio
import settings


def get_api_connections():
    apis = {}
    for conn_name, conn_details in settings.connections.items():
        auth = tweepy.OAuthHandler(conn_details['consumer_key'], conn_details['consumer_secret'])
        auth.set_access_token(conn_details['access_key'], conn_details['access_secret'])
        apis.update({conn_name: tweepy.API(auth, wait_on_rate_limit=True)})
        print('{} API successfully connected!'.format(conn_name))
    return apis


def reconnect_api(conn_name):
    conn_details = settings.connections[conn_name]
    auth = tweepy.OAuthHandler(conn_details['consumer_key'], conn_details['consumer_secret'])
    auth.set_access_token(conn_details['access_key'], conn_details['access_secret'])
    api = tweepy.API(auth, wait_on_rate_limit=True)
    print('{} API successfully connected!'.format(conn_name))
    return api


def batches(lst, n=100):
    batches = []
    for i in range(0, len(lst), n):
        batches.append(lst[i:i+n])
    return batches


def read_users_friends_followers(folder_name=None):
    print("Reading user's friends and followers")
    if folder_name is not None:
        user_ids_dir = settings.USER_IDS_DIR.replace(settings.folder_name, folder_name)
    else:
        user_ids_dir = settings.USER_IDS_DIR
    content = {}
    for fn in tqdm(os.listdir(user_ids_dir)):
        file_content = fileio.read_content(os.path.join(user_ids_dir, fn), 'json')
        content.update(file_content)
    return content


def get_users_friends_followers_ids(folder_name):
    users_friends_followers = read_users_friends_followers(folder_name)
    print("Collecting user's friends and follower IDs")
    users_friends_followers_ids = set(map(int, users_friends_followers.keys()))
    for _, item in tqdm(users_friends_followers.items()):
        users_friends_followers_ids = users_friends_followers_ids.union(item['friends'])
        users_friends_followers_ids = users_friends_followers_ids.union(item['followers'])
    return users_friends_followers_ids


def get_baseline_user_ids(processed_filepath=settings.PROCESSED_USER_IDS, users_friends_followers=False):
    baseline_user_ids = set(fileio.read_content(settings.BASELINE_USER_IDS, 'json'))
    
    if users_friends_followers:
        users_friends_followers_ids = get_users_friends_followers_ids()
        baseline_user_ids.difference_update(users_friends_followers_ids)
        
    missing_user_ids = set(fileio.read_content(settings.MISSING_USER_IDS, 'json'))
    processed_user_ids = set(fileio.read_content(processed_filepath, 'json'))
    
    baseline_user_ids.difference_update(missing_user_ids)
    baseline_user_ids.difference_update(processed_user_ids)
    return baseline_user_ids


def get_twitter_endpoint(conn_name, api, method_name, user_id, retry_max=3, retry_delay=3, **kwargs):
    """get_twitter_endpoint
    Generates a tweepy.API method using `api` and `conn_name`,
    requests, processes response and returns API content.
    Used with `get_friend_ids` and `get_follower_ids`

    Args:
        conn_name (str): Connection name defined in settings
        api (tweepy.API): tweepy.API object
        method_name ([type]): tweepy.API method name
        user_id (int): Fetch the provided user_id's friends and followers
        retry_max (int, optional): Failed request max no. of retries. Defaults to 3.
        retry_delay (int, optional): Failed request retry. Defaults to 3.

    Returns:
        list|dict, int: (content, user_id) user_id exists if it is not found or request is unauthorized
    """
    content = []
    
    method = getattr(api, method_name)

    retry_num = 0
    while retry_num < retry_max:
        try:
            content = method(user_id=user_id, **kwargs)
            return content, None
        except tweepy.errors.NotFound: # 404
            return content, user_id
        except tweepy.errors.Unauthorized: # 401
            return content, user_id
        except requests.exceptions.ConnectionError:
            api = reconnect_api(conn_name)
            method = getattr(api, method_name)
            delay = retry_delay*(retry_num+1)
            print("\nConnectionError: try #{}, {}s delay".format(retry_num+1, delay))
            time.sleep(delay)
            retry_num += 1
        except tweepy.errors.TweepyException:
            api = reconnect_api(conn_name)
            method = getattr(api, method_name)
            delay = retry_delay*(retry_num+1)
            print("\nTweepyException: try #{}, {}s delay".format(retry_num+1, delay))
            time.sleep(delay)
            retry_num += 1
    
    return content, None


def get_twitter_lookup_users(conn_name, api, user_ids, retry_max=3, retry_delay=3):
    """get_twitter_lookup_users
    Generates a tweepy.API method using `api` and `conn_name`,
    requests, processes response and returns API content.
    Used with `get_friend_ids` and `get_follower_ids`

    Args:
        conn_name (str): Connection name defined in settings
        api (tweepy.API): tweepy.API object
        user_ids (list): List of user_id's to fetch objects for
        retry_max (int, optional): Failed request max no. of retries. Defaults to 3.
        retry_delay (int, optional): Failed request retry. Defaults to 3.

    Returns:
        list: User objects list
    """
    
    retry_num = 0
    while retry_num < retry_max:
        try:
            batch_users = api.lookup_users(user_id=user_ids)
        except tweepy.errors.TwitterServerError: # 503
            print("\nTwitterServerError: try #{}, {}s delay".format(retry_num+1, retry_delay))
            time.sleep(retry_delay)
            retry_num += 1
        except tweepy.errors.TweepyException:
            api = reconnect_api(conn_name)
            print("\nTweepyException: try #{}, {}s delay".format(retry_num+1, retry_delay))
            time.sleep(retry_delay)
            retry_num += 1
        except requests.exceptions.ConnectionError:
            api = reconnect_api(conn_name)
            print("\nConnectionError: try #{}, {}s delay".format(retry_num+1, retry_delay))
            time.sleep(retry_delay)
            retry_num += 1
        else:
            _content = [user._json for user in batch_users]
            content = [
                {
                    'user_id': user.get('id'), 
                    'location': user.get('location'),
                    'screen_name': user.get('screen_name'), 
                    'name': user.get('name'), 
                    'statuses_count': user.get('statuses_count'), 
                    'friends_count': user.get('friends_count'), 
                    'followers_count': user.get('followers_count'),
                    'description': user.get('description'),
                    'created_at': user.get('created_at'), 
                    'verified': user.get('verified'),
                    'protected': user.get('protected')
                } for user in _content
            ]
            return content
