import os
from tqdm import tqdm

from . import fileio
from twitter_scraper import settings


def batches(lst, n=100):
    batches = []
    for i in range(0, len(lst), n):
        batches.append(lst[i:i+n])
    return batches


def get_tweet_max_id(user_id):
    user_tweets = fileio.read_content(os.path.join(settings.USER_TWEETS_DIR, '{}.json'.format(user_id)), 'json')
    if user_tweets:
        latest_tweet = max(user_tweets, key=lambda x: x['id'])
        return latest_tweet['id']
    return None


def _read_users_friends_followers(folder_name=None):
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


def get_users_friends_followers_ids(folder_name=None):
    users_friends_followers = _read_users_friends_followers(folder_name)
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
