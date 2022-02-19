# %%
import re
import csv
import os
import time
import string
import pandas as pd
from tqdm import tqdm

import utils
from utils import fileio
from twitter_scraper import settings

logger = utils.get_logger(__file__)

USER_OBJS_CSV = os.path.join(settings.USER_OBJS_DIR, 'user-objs.csv')
LOCATIONS_JSON = os.path.join(settings.INPUT_DIR, 'locations.json')

locations = pd.read_json(LOCATIONS_JSON)[0]
accepted_chars = string.ascii_lowercase + 'čšćžđ'

USER_DTYPE = {
    'user_id':          'int',
    'user_id_str':      'string',
    'name':             'string',
    'screen_name':      'string',
    'location':         'string',
    # "profile_location": 'object',
    # 'derived':          'string',
    # 'url':              'string',
    'description':      'string',
    'protected':        'boolean',
    'verified':         'boolean',
    'followers_count':  'int',
    'friends_count':    'int',
    'listed_count':     'int',
    'favourites_count': 'int',
    'statuses_count':   'int',
    'created_at':       'str',
    # 'profile_banner_url':      'string',
    # 'profile_image_url_https': 'string',
    # 'default_profile':         'object',
    # 'default_profile_image':   'string',
    # 'withheld_in_countries':   'object',
    # 'withheld_scope':          'object',

    ### Custom columns
    'is_croatian':      'bool',
    'clean_location':   'string',
}

# %%
def get_users_df():
    #users_df = pd.read_csv('C:\\Users\\AndreaHrelja\\Documents\\Faks\\twitter_scraper\\output\\users\\objs\\2022-02-03\\user-objs.csv')
    users_df = pd.read_csv(USER_OBJS_CSV, dtype=USER_DTYPE)
    users_df = users_df[users_df['protected'] == False]
    users_df['created_at'] = pd.to_datetime(users_df['created_at'], format='%a %b %d %H:%M:%S %z %Y') # 30s
    users_df['location'] = users_df['location'].fillna('').transform(lambda x: x.replace(re.search(r'[ ]+', x).group(), ' ').strip() if re.search(r'[ ]+', x) else x)
    return users_df


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
                new_location = new_location.replace(char, ' ')
        
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
    
    if location.lower() in (loc.lower() for loc in locations):
        return True
    else:
        return any(cro_loc in location.lower() for cro_loc in cro_locations)

def transform_users_df(users_df):
    users_df['is_croatian'] = users_df['location'].fillna('').transform(is_croatian)
    users_df['clean_location'] = users_df[users_df['is_croatian'] == True]['location'].transform(clean_location)
    users_df = users_df[
        (users_df['is_croatian'] == True)
        & (users_df['statuses_count'] > 10)
        & (users_df['friends_count'] > 10)
        & (users_df['friends_count'] < 5000)
        & (users_df['followers_count'] > 10)
        #& (users_df['followers_count'] < 5000)
    ].sort_values(by='followers_count')
    return users_df[USER_DTYPE.keys()].astype(USER_DTYPE)

# %%
def update_baseline():
    users_df = get_users_df()
    baseline = set(fileio.read_content(settings.BASELINE_USER_IDS, 'json'))
    baseline = baseline.union(users_df.user_id.values)
    fileio.write_content(settings.BASELINE_USER_IDS, list(baseline), 'json', overwrite=True)


def users():
    start_time = time.time()
    
    utils.mkdir(os.path.dirname(settings.USERS_CSV))

    logger.info("Cleaning Users")
    users_df = get_users_df()
    users_df = transform_users_df(users_df)
    users_df.to_csv(settings.USERS_CSV, index=False, quoting=csv.QUOTE_NONNUMERIC)
    logger.info("Done cleaning Users")
    logger.info("User model saved: {}".format(settings.USERS_CSV))

    end_time = time.time()
    logger.info("Time elapsed: {} min".format((end_time - start_time)/60))

# %%
if __name__ == '__main__':
    users()
    #update_baseline()