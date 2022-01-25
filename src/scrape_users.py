from cv2 import batchDistance
import tweepy
import time
import os
import pandas as pd
from tqdm import tqdm

import utils
import settings

start_user_ids = [146153494] # andhrelja
api = utils.connect_to_twitter()


def get_followers_ids(user_id):
    followers_ids = []
    
    try:
        root = api.get_user(user_id=user_id)
    except tweepy.errors.NotFound:
        print("User {} not found, skipping this step".format(user_id))
        return followers_ids

    twitter_screen_name = root.screen_name
    
    #print('get_followers_ids function working on: ' + twitter_screen_name)
    
    try:
        cursor = tweepy.Cursor(api.get_follower_ids, screen_name=twitter_screen_name)
    except BaseException as e:
        print('failed on_status,',str(e))
        time.sleep(3)

    for page in cursor.pages():
        followers_ids.extend(page)
    
    #print(str(twitter_screen_name) + " has " + str(len(followers_ids)) + " followers")
    return followers_ids


def get_friends_ids(user_id):
    friends_ids = []
    
    try:
        root = api.get_user(user_id=user_id)
    except tweepy.errors.NotFound:
        print("User {} not found, skipping this step".format(user_id))
        return friends_ids
    
    twitter_screen_name = root.screen_name
    
    #print('get_friends_ids function working on: ' + twitter_screen_name)
    
    try:
        cursor = tweepy.Cursor(api.get_friend_ids, screen_name=twitter_screen_name)
    except BaseException as e:
        print('failed on_status,',str(e))
        time.sleep(3)

    for page in cursor.pages():
        friends_ids.extend(page)
    
    #print(str(twitter_screen_name) + " is following " + str(len(friends_ids)) + " friends")
    return friends_ids


def _get_start_user_ids():
    users_csv_path = os.path.join(settings.INPUT_DIR, 'users.csv')
    if os.path.isfile(users_csv_path):
        df = pd.read_csv(users_csv_path)
        return set(df.user_id)
    else:
        return set(start_user_ids)

def _get_lst_batches(lst, n=100):
    batches = []
    for i in range(0, len(lst), n):
        batches.append(lst[i:i+n])
    return batches


def scrape_users():
    all_user_ids = _get_start_user_ids()
    
    print("Collecting friends and follower IDs for start_user_ids...")
    for user_id in tqdm(all_user_ids):
        try:
            friend_ids = get_friends_ids(user_id)
            follower_ids = get_followers_ids(user_id)
        except tweepy.errors.TooManyRequests:
            print("Rate limit exceeded. Sleeping for 15 minutes")
            time.sleep(60*15)
            
            friend_ids = get_friends_ids(user_id)
            follower_ids = get_followers_ids(user_id)
        
        all_user_ids = all_user_ids.union(set(friend_ids))
        all_user_ids = all_user_ids.union(set(follower_ids))
    
    print("Collecting friends and follower objects...")
    all_users = []
    for user_ids in tqdm(_get_lst_batches(all_user_ids, 100)):
        try:
            batch_users = api.lookup_users(user_id=user_ids)
        except tweepy.errors.TooManyRequests:
            print("Rate limit exceeded. Sleeping for 15 minutes")
            time.sleep(60*15)
            
            batch_users = api.lookup_users(user_id=user_ids)
        
        all_users.extend(batch_users)
    
    user_info_csv_path = os.path.join(settings.INPUT_DIR, 'user_info.csv')
    df = pd.DataFrame(all_users)
    df.to_csv(user_info_csv_path, encoding='utf-8')
    print("Done")


if __name__ == '__main__':
    scrape_users()
