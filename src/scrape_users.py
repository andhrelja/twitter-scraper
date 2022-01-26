from tqdm import tqdm
import os
import time
import datetime as dt
import pandas as pd
import tweepy

import fileio as io
import utils
import settings

USERS_CSV = os.path.join(settings.INPUT_DIR, 'users.csv')
USERS_INFO_CSV = os.path.join(settings.INPUT_DIR, 'users-info.csv')

api = utils.connect_to_twitter()


def get_twitter_endpoint(method, user_id):
    content = []
    cursor = tweepy.Cursor(method=method, user_id=user_id)
    
    for page in cursor.pages():
        content.extend(page)

    return content


def _get_start_user_ids():
    users_csv_path = os.path.join(settings.INPUT_DIR, 'users.csv')
    if os.path.isfile(users_csv_path):
        df = pd.read_csv(users_csv_path)
        return set(df.user_id)
    else:
        return set([146153494]) # andhrelja

def _get_lst_batches(lst, n=100):
    batches = []
    for i in range(0, len(lst), n):
        batches.append(lst[i:i+n])
    return batches

def collect_user_ids(all_user_ids):
    print("Collecting friends and follower IDs for start_user_ids...")
    for user_id in tqdm(all_user_ids):
        try:
            friend_ids = get_twitter_endpoint(api.get_friend_ids, user_id)
            follower_ids = get_twitter_endpoint(api.get_follower_ids, user_id)
        except tweepy.errors.TooManyRequests:
            print("\nRate limit exceeded. Sleeping for 15 minutes")
            time.sleep(60*15)
            
            friend_ids = get_twitter_endpoint(api.get_friend_ids, user_id)
            follower_ids = get_twitter_endpoint(api.get_follower_ids, user_id)
        
        all_user_ids = all_user_ids.union(set(friend_ids))
        all_user_ids = all_user_ids.union(set(follower_ids))
    return all_user_ids


def collect_user_objs(all_user_ids):
    print("Collecting friends and follower objects...")
    all_users = []
    for user_ids in tqdm(_get_lst_batches(list(all_user_ids), 100)):
        try:
            batch_users = api.lookup_users(user_id=user_ids)
        except tweepy.errors.TooManyRequests: # 429
            print("\nRate limit exceeded. Sleeping for 15 minutes")
            time.sleep(60*15)
            batch_users = api.lookup_users(user_id=user_ids)
        except tweepy.errors.TwitterServerError: # 503
            print("\nService unavailable. Sleeping for 10 seconds")
            time.sleep(10)
            batch_users = api.lookup_users(user_id=user_ids)
        
        content = [user._json for user in batch_users]
        io.write_content(USERS_INFO_CSV, content, 'csv', metadata={'created_at_dttm': dt.datetime.now()})
        all_users.extend(content)
    return all_users

def scrape_users(skip_user_ids=False):
    start_user_ids = _get_start_user_ids()
    if skip_user_ids:
        all_user_ids = start_user_ids
    else:
        all_user_ids = collect_user_ids(start_user_ids)
    
    collect_user_objs(all_user_ids)
    print("Done")


if __name__ == '__main__':
    scrape_users(skip_user_ids=True)
