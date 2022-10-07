# %%
import re
import csv
import os
import time
import string
import pandas as pd

from twitter_scraper import utils
from twitter_scraper import settings
from twitter_scraper.utils import fileio

logger = utils.get_logger(__file__)

USER_OBJS_CSV = os.path.join(settings.USER_OBJS_DIR, 'user-objs.csv')
LOCATIONS_JSON = os.path.join(settings.INPUT_DIR, 'locations.json')

USER_DTYPE = {
    'user_id':          'int64',
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
def is_croatian(location):
    locations = pd.read_json(LOCATIONS_JSON)[0]
    
    if location == '':
        return False
    
    cro_locations = ('croa', 'hrvat')
    
    if location.lower() in (loc.lower() for loc in locations):
        return True
    else:
        return any(cro_loc in location.lower() for cro_loc in cro_locations)


def clean_location(location):
    if location == '':
        return location
    
    location_lower = location.lower()
    location_names = ('republic of croatia', 'republika hrvatska', 'hrvatska', 'croatia', 'croacia', 'croatie')
    accepted_chars = string.ascii_lowercase + 'čšćžđ'
    
    if re.search(r'\s+', location):
        location_lower = re.sub(r'\s+', ' ', location).strip().lower()
    
    for name in location_names:
        if name in location.lower():
            return 'Hrvatska'
    
    # for char in location.lower():
    #     if char not in accepted_chars + ' ':
    #         location_lower = location_lower.replace(char, ' ')
    
    if location_lower == '':
        location_lower = 'hrvatska'
    return location_lower.title()

def transform_users_df(users_df):
    users_df['created_at'] = pd.to_datetime(users_df['created_at'], format='%a %b %d %H:%M:%S %z %Y')
    users_df['location'] = users_df['location'].fillna('').transform(lambda x: re.sub(r'\s+', ' ', x).strip())
    users_df['is_croatian'] = users_df['location'].transform(is_croatian)
    users_df['clean_location'] = users_df.loc[users_df['is_croatian'] == True, 'location'].transform(clean_location)

    if settings.DEBUG:
        filters = ((users_df['protected'] == False)
            & (users_df['is_croatian'] == True)
            # & (users_df['statuses_count'] > 10)
            # & (users_df['friends_count'] > 10)
            # & (users_df['friends_count'] < 5000)
            # & (users_df['followers_count'] > 10)
            & (users_df['followers_count'] < 5000)
        )
    else:
        filters = ((users_df['protected'] == False)
            & (users_df['is_croatian'] == True)
            & (users_df['statuses_count'] > 10)
            & (users_df['friends_count'] > 10)
            & (users_df['friends_count'] < 5000)
            & (users_df['followers_count'] > 10)
            # & (users_df['followers_count'] < 5000)
        )
    users_df = users_df[filters].sort_values(by='followers_count')
    return users_df[USER_DTYPE.keys()].astype(USER_DTYPE)

# %%

def update_filtered_baseline(users_df):
    archive_baseline_len = len(utils.get_baseline_user_ids())
    baseline_user_ids = list(map(int, users_df.user_id.values))
    utils.archive_baseline(prefix='clean.users')
    fileio.write_content(settings.BASELINE_USER_IDS, baseline_user_ids, 'json', overwrite=True)
    logger.info("Filtered baseline from {:,} to {:,} records".format(archive_baseline_len, len(baseline_user_ids)))
    

# %%
def users():
    start_time = time.time()
    
    utils.mkdir(os.path.dirname(settings.USERS_CSV))

    logger.info("START - Cleaning Users ...")
    users_df = pd.read_csv(USER_OBJS_CSV, dtype=USER_DTYPE)
    users_df = transform_users_df(users_df)

    users_df.to_csv(settings.USERS_CSV, index=False, quoting=csv.QUOTE_NONNUMERIC)
    logger.info("Wrote clean User model to {}".format(settings.USERS_CSV))

    update_filtered_baseline(users_df)

    end_time = time.time()
    logger.info("User model saved: {}".format(settings.USERS_CSV))
    logger.info("END - Done cleaning Users")
    logger.info("Time elapsed: {} min".format(round((end_time - start_time)/60, 2)))

# %%
if __name__ == '__main__':
    users()