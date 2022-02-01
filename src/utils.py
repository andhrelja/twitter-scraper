import tweepy

import settings


def get_api_connections():
    apis = []
    for conn_name, conn_details in settings.connections.items():
        auth = tweepy.OAuthHandler(conn_details['consumer_key'], conn_details['consumer_secret'])
        auth.set_access_token(conn_details['access_key'], conn_details['access_secret'])
        apis.append({conn_name: tweepy.API(auth, wait_on_rate_limit=True)})
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
