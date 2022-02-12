# %%
import re
import os
import string
import pandas as pd
import datetime as dt

import utils.fileio as fileio
from twitter_scraper import settings

USER_OBJS_CSV = os.path.join(settings.USER_OBJS_DIR, 'user-objs.csv')
LOCATIONS_JSON = os.path.join(settings.INPUT_DIR, 'locations.json')

locations = pd.read_json(LOCATIONS_JSON)[0]
accepted_chars = string.ascii_lowercase + 'čšćžđ'


def get_user_df():
    #user_df = pd.read_csv('C:\\Users\\AndreaHrelja\\Documents\\Faks\\twitter_scraper\\output\\users\\objs\\2022-02-03\\user-objs.csv')
    user_df = pd.read_csv(USER_OBJS_CSV)
    user_df = user_df[user_df['protected'] == False]
    user_df['created_at'] = pd.to_datetime(user_df['created_at'], format='%a %b %d %H:%M:%S %z %Y') # 30s
    return user_df

# %%

def clean_location(location):
    if location == '':
        return location
    
    new_location = location.lower()
    location_names = ('republic of croatia', 'republika hrvatska', 'hrvatska', 'croatia', 'croacia', 'croatie')
    
    if re.search(r'[ ]+', location):
        new_location = new_location.replace(re.search(r'[ ]+', location).group(), ' ').strip()
    
    for name in location_names:
        if new_location == name:
            return 'Hrvatska'
    
        for char in location.lower():
            if char not in accepted_chars + ' ':
                new_location = new_location.replace(char, '')
        
        if name in location.lower():
            new_location = new_location.replace(name, '')
        new_location = new_location.strip()
        
    if new_location == '':
        new_location = 'Hrvatska'
    return new_location.title()


def is_croatian(location):
    global locations
    
    if location == '':
        return False
    
    cro_locations = ('croa', 'hrvat')
    
    if location.lower() in locations:
        return True
    else:
        return any(cro_loc in location.lower() for cro_loc in cro_locations)

def transform_user_df(user_df):
    user_df['is_croatian'] = user_df['location'].fillna('').transform(is_croatian)
    user_df['clean_location'] = user_df[user_df['is_croatian'] == True]['location'].transform(clean_location)
    user_df = user_df[
        (user_df['is_croatian'] == True)
        & (user_df['statuses_count'] > 10)
        & (user_df['friends_count'] > 10)
        & (user_df['friends_count'] < 5000)
        & (user_df['followers_count'] > 10)
        #& (user_df['followers_count'] < 5000)
    ].sort_values(by='followers_count')
    return user_df

#user.user_id.to_json('../../input/new-baseline-user-ids.json', orient='records', indent=2)

# %%

def generate_edges_df(user_df):
    not_found = 0
    users_data = []
    total_users = len(user_df.user_id.unique())
    
    for user_id in user_df.user_id.unique():
        user_path = os.path.join(settings.USER_IDS_DIR, '{}.json'.format(user_id))
        if os.path.exists(user_path):
            user = fileio.read_content(user_path, 'json')
            for follower in user.get('followers', []):
                users_data.append({
                    'source': str(follower),
                    'target': str(user_id)
                })
        else:
            not_found += 1
    
    print("Found {}/{} users".format(total_users-not_found, total_users))
    return pd.DataFrame(users_data)


def users():
    print("{} - Cleaning users ...".format(dt.datetime.now()))
    
    edges_graph_dir, _ = os.path.split(settings.EDGES_CSV)
    users_csv_dir, _ = os.path.split(settings.USERS_CSV)
    if not os.path.exists(edges_graph_dir):
        os.mkdir(edges_graph_dir)
    if not os.path.exists(users_csv_dir):
        os.mkdir(users_csv_dir)
    
    user_df = get_user_df()
    user_df = transform_user_df(user_df)
    user_df.to_csv(settings.USERS_CSV, index=False)
    
    edges_df = generate_edges_df(user_df)
    edges_df.to_csv(settings.EDGES_CSV, index=False)
