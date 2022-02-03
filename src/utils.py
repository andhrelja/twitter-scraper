import time
import tweepy
import requests.exceptions

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



def get_twitter_endpoint(conn_name, api, method_name, user_id, retry_max=3, retry_delay=3):
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
            content = method(user_id=user_id)
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
