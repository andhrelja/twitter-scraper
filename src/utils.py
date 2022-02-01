import os
import json
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


def get_collected_user_ids():
    print("Getting collected user ids", end="...")
    latest_scrape_date = max(filter(None, [item if os.path.isdir(os.path.join(settings.INPUT_DIR, item)) else None for item in os.listdir(settings.INPUT_DIR)]))
    
    content = {}
    for file_name in os.listdir(os.path.join(settings.INPUT_DIR, latest_scrape_date)):
        file_path = os.path.join(settings.INPUT_DIR, latest_scrape_date, file_name)
        with open(file_path, 'r') as f:
            content.update(json.load(f))
    
    all_user_ids = set()
    for user_id, user_info in content.items():
        all_user_ids.add(user_id)
        all_user_ids = all_user_ids.union(user_info.get('friends'))
        all_user_ids = all_user_ids.union(user_info.get('followers'))
    
    print("Done")
    return all_user_ids


def batches(lst, n=100):
    batches = []
    for i in range(0, len(lst), n):
        batches.append(lst[i:i+n])
    return batches
