import time
import tweepy
import requests.exceptions

from . import utils
from twitter_scraper import settings

logger = utils.get_logger(__file__)

def get_api_connections():
    apis = {}
    for conn_name, conn_details in settings.connections.items():
        auth = tweepy.OAuthHandler(conn_details['consumer_key'], conn_details['consumer_secret'])
        auth.set_access_token(conn_details['access_key'], conn_details['access_secret'])
        apis.update({conn_name: tweepy.API(auth, wait_on_rate_limit=True)})
    logger.info('{} APIs successfully connected!'.format(len(apis)))
    return apis


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
            retry_num += 1
            delay = retry_delay*(retry_num)
            logger.warning("ConnectionError: try #{}, {}s delay".format(retry_num, delay))
            time.sleep(delay)

        except tweepy.errors.TweepyException:
            api = reconnect_api(conn_name)
            method = getattr(api, method_name)
            retry_num += 1
            delay = retry_delay*(retry_num)
            logger.warning("TweepyException: try #{}, {}s delay".format(retry_num, delay))
            time.sleep(delay)
            
    
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
            retry_num += 1
            delay = retry_delay*(retry_num)
            logger.warning("TwitterServerError: try #{}, {}s delay".format(retry_num+1, retry_delay))
            time.sleep(delay)
            
        except tweepy.errors.TweepyException:
            api = reconnect_api(conn_name)
            retry_num += 1
            delay = retry_delay*(retry_num)
            logger.warning("TweepyException: try #{}, {}s delay".format(retry_num+1, retry_delay))
            time.sleep(delay)
            
        except requests.exceptions.ConnectionError:
            api = reconnect_api(conn_name)
            retry_num += 1
            delay = retry_delay*(retry_num)
            logger.warning("ConnectionError: try #{}, {}s delay".format(retry_num+1, retry_delay))
            time.sleep(delay)
            
        else:
            return batch_users
            


def reconnect_api(conn_name):
    conn_details = settings.connections[conn_name]
    auth = tweepy.OAuthHandler(conn_details['consumer_key'], conn_details['consumer_secret'])
    auth.set_access_token(conn_details['access_key'], conn_details['access_secret'])
    api = tweepy.API(auth, wait_on_rate_limit=True)
    logger.info('{} API successfully connected!'.format(conn_name))
    return api
