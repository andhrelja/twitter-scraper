import os
import tweepy
import fileio

from scrape_user_ids import INPUT_DIR
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


def get_output_user_ids():
    output_user_ids = set()
    for file_name in os.listdir(INPUT_DIR):
        user_id = file_name.replace('.json', '')
        output_user_ids.add(int(user_id))
    return output_user_ids

def get_new_baseline_ids():
    new_baseline_ids = fileio.read_content(os.path.join(settings.OUTPUT_DIR, 'baseline-user-ids.json'), 'json')
    baseline_user_ids = get_output_user_ids()
    
    new_baseline_ids = set(new_baseline_ids)
    new_baseline_ids.difference_update(baseline_user_ids)
    return new_baseline_ids 

def get_initial_user_ids():
    baseline_user_ids = fileio.read_content(settings.BASELINE_USER_IDS, 'json')
    missing_user_ids = fileio.read_content(settings.MISSING_USER_IDS, 'json')
    processed_user_ids = fileio.read_content(settings.PROCESSED_USER_IDS, 'json')
    
    initial_user_ids = set(baseline_user_ids)
    initial_user_ids.difference_update(missing_user_ids)
    initial_user_ids.difference_update(processed_user_ids)
    return initial_user_ids
