"""scrape_users.py

Inputs:
- user_ids (~/scrape_tweets/profiles_get_tweets.csv || ~/input/users.csv)
- user_info (~/input/users-info.csv)
    * user information schema (required columns)

Workflow:
1. Collect new users
    - get existing user_ids (input)
    - for each user_id:
        * collect all_followers (endpoint: get_follower_ids)
        * collect all_friends (endpoint: get_friend_ids)
    - create a new list of user_ids (user_ids + all_followers + all_friends): all_user_ids
    - overwrite existing user_ids
2. Collect user information
    - get existing user_info (input)
    - exclude all_user_ids with existing user_ids from user_info
    - collect all_user_info (endpoint: user_lookup)
    - create a new list of user_info (all_user_info) and apply the user information schema
    - overwrite existing user_info
"""

from tqdm import tqdm
import os
import time
import tweepy
import datetime as dt

import fileio as io
import utils
import settings

today = dt.date.today()
folder_name = "{}-{}-{}".format(today.year, today.month, today.day)

INPUT_DIR = os.path.join(settings.INPUT_DIR, folder_name)
if not os.path.exists(INPUT_DIR):
    os.mkdir(INPUT_DIR)

USERS_CSV = os.path.join(INPUT_DIR, 'users.csv')
USERS_INFO_CSV = os.path.join(INPUT_DIR, 'users-info.csv')

USER_IDS_CSV = os.path.join(INPUT_DIR, 'users-ids.csv')
USER_IDS_JSON = os.path.join(INPUT_DIR, 'users-ids.json')
MISSING_USERS_JSON = os.path.join(INPUT_DIR, 'missing-user-ids.json')

api = utils.connect_to_twitter(wait_on_rate_limit=True)


def get_paginated_twitter_content(api_method, user_id):
    content = []
    cursor = tweepy.Cursor(method=api_method, user_id=user_id)

    try:
        for page in cursor.pages():
            content.extend(page)
    except tweepy.errors.NotFound: # 404
        print("\nUser {} not found".format(user_id))
        return content, user_id
    except tweepy.errors.Unauthorized: # 401
        print("\nUser {} unauthorized".format(user_id))
        return content, user_id

    return content, None


def collect_user_ids(all_user_ids):
    print("Collecting friends and follower IDs for start_user_ids...")
    for user_ids in tqdm(utils.batches(list(all_user_ids), 15)):
        print("\n {}".format(dt.datetime.now()))
        output_dict = {}
        missing_users = set()
        for user_id in user_ids:
            friend_ids, inactive_user = get_paginated_twitter_content(api.get_friend_ids, user_id)
            if inactive_user and not friend_ids:
                missing_users.add(inactive_user)
                continue
            follower_ids, _ = get_paginated_twitter_content(api.get_follower_ids, user_id)
            
            
            output_dict[str(user_id)] = {
                'num_friends': len(friend_ids),
                'num_followers': len(follower_ids),
                'friends': friend_ids,
                'followers': follower_ids
            }
            
        io.write_content(USER_IDS_JSON, output_dict, 'json')
        io.write_content(MISSING_USERS_JSON, list(missing_users), 'json')


def collect_user_objs(all_user_ids):
    print("Collecting friends and follower objects...")
    for user_ids in tqdm(utils.batches(list(all_user_ids), 100)):
        try:
            batch_users = api.lookup_users(user_id=user_ids)
        except tweepy.errors.TwitterServerError: # 503
            print("\nService unavailable. Sleeping for 10 seconds")
            time.sleep(10)
            batch_users = api.lookup_users(user_id=user_ids)
        
        _content = [user._json for user in batch_users]
        content = [
            {
                'user_id': user.get('id'), 
                'screen_name': user.get('screen_name'), 
                'created_at': user.get('created_at'), 
                'verified': user.get('verified'), 
                'url': user.get('url'), 
                'name': user.get('name'), 
                'description': user.get('description'),
                'statuses_count': user.get('statuses_count'), 
                'friends_count': user.get('friends_count'), 
                'followers_count': user.get('followers_count'), 
                'location': user.get('location')
            } for user in _content
        ]
        
        io.write_content(USERS_INFO_CSV, content, 'csv')


def get_user_ids_from_json(content):
    all_user_ids = set()
    for user_id, user_info in content.items():
        all_user_ids.add(user_id)
        all_user_ids = all_user_ids.union(user_info.get('friends'))
        all_user_ids = all_user_ids.union(user_info.get('followers'))
    return all_user_ids


def get_initial_user_ids():
    if os.path.isfile(USERS_CSV):
        user_ids = io.read_content(USERS_CSV, 'csv', column='user_id')
        return set(map(int, user_ids))
    else:
        return set([146153494]) # andhrelja


def scrape_users():
    print("Start time {}".format(dt.datetime.now()))
    start_time = time.time()
    json_content = io.read_content(USER_IDS_JSON, 'json')
    missing_user_ids = io.read_content(MISSING_USERS_JSON, 'json')
    
    initial_user_ids = get_initial_user_ids()
    initial_user_ids.difference_update(map(int, json_content.keys()))
    initial_user_ids.difference_update(set(missing_user_ids))
    collect_user_ids(initial_user_ids)
    
    json_content = io.read_content(USER_IDS_JSON, 'json')
    all_user_ids = get_user_ids_from_json(json_content)
    collect_user_objs(all_user_ids)
    
    end_time = time.time()
    print("End time {}".format(dt.datetime.now()))
    print("Done in {} seconds".format(end_time))


if __name__ == '__main__':
    scrape_users()
