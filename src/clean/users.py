# %%
import re
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
    "profile_location": 'object',
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
    users_df = pd.read_csv(USER_OBJS_CSV)
    users_df = users_df[users_df['protected'] == False]
    users_df['created_at'] = pd.to_datetime(users_df['created_at'], format='%a %b %d %H:%M:%S %z %Y') # 30s
    users_df['location'] = users_df['location'].transform(lambda x: x.replace(re.search(r'[ ]+', x).group(), ' ') if re.search(r'[ ]+', x) else x)
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
    return users_df.astype(USER_DTYPE)


def get_edges_df(nodes_df):
    not_found = 0
    users_data = []
    total_users = len(nodes_df.user_id.unique())
    
    for user_id in tqdm(nodes_df.user_id.unique()):
        user_path = os.path.join(settings.USER_IDS_DIR, '{}.json'.format(user_id))
        if os.path.exists(user_path):
            user = fileio.read_content(user_path, 'json')
            for follower in user[str(user_id)].get('followers', []):
                if follower in nodes_df.user_id.unique():
                    users_data.append({
                        'source': int(follower),
                        'target': int(user_id)
                    })
        else:
            not_found += 1
    
    found = total_users-not_found
    edges_df = pd.DataFrame(users_data, columns=['source', 'target'])
    return edges_df, found, total_users

# %%
def update_baseline():
    users_df = get_users_df()
    baseline = set(fileio.read_content(settings.BASELINE_USER_IDS, 'json'))
    baseline = baseline.union(users_df.user_id.values)
    fileio.write_content(settings.BASELINE_USER_IDS, list(baseline), 'json', overwrite=True)


def users(edges=False):
    start_time = time.time()
    
    edges_graph_dir, _ = os.path.split(settings.EDGES_CSV)
    users_csv_dir, _ = os.path.split(settings.USERS_CSV)
    utils.mkdir(users_csv_dir)
    utils.mkdir(edges_graph_dir)

    logger.info("Cleaning Users")
    users_df = get_users_df()
    users_df = transform_users_df(users_df)
    users_df.to_csv(settings.USERS_CSV, index=False)
    logger.info("Done cleaning Users")
    logger.info("User model saved: {}".format(settings.USERS_CSV))
    
    if edges:
        logger.info("Creating Edges df, this may take a while")
        edges_df, found, total_users = get_edges_df(users_df)
        edges_df.to_csv(settings.EDGES_CSV, index=False)
        logger.info("Done creating Edges df:\n\t- found {}/{} nodes\n\t- found edges for {}/{} nodes".format(found, total_users, len(edges_df.source.unique()), found))
    logger.info("Graph edges saved: {}".format(settings.EDGES_CSV))

    end_time = time.time()
    logger.info("Time elapsed: {} min".format((end_time - start_time)/60))

# %%
if __name__ == '__main__':
    users(edges=False)
    #update_baseline()