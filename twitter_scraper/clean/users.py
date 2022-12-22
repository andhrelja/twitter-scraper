# %%
import re
import csv
import os
import pandas as pd
import datetime as dt
from tqdm import tqdm

from twitter_scraper import utils
from twitter_scraper import settings
from twitter_scraper.utils import fileio

logger = utils.get_logger(__file__)
locations = fileio.read_content(settings.LOCATIONS_HR, 'json')

# %%
def update_filtered_baseline():
    if not os.path.exists(settings.CLEAN_USERS_CSV):
        logger.warning("STOP - Baseline was not updated, missing scraped users")
        return
    
    users_df = pd.read_csv(settings.CLEAN_USERS_CSV)
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
            # & (users_df['friends_count'] < 5000)
            & (users_df['followers_count'] > 10)
            # & (users_df['followers_count'] < 5000)
        )
    users_df = users_df[filters].sort_values(by='followers_count', ascending=False)

    archive_baseline_len = len(utils.get_baseline_user_ids())
    baseline_user_ids = list(map(int, users_df.user_id.values))
    
    utils.archive_baseline(prefix='clean.users')
    fileio.write_content(settings.BASELINE_USER_IDS, baseline_user_ids, 'json', overwrite=True)
    fileio.write_content(
        path=os.path.join(settings.LOGS_DIR, '{}.json'.format(settings.folder_name)), 
        content={'cro_users_len': len(users_df)},
        file_type='json'
    )
    logger.info("Filtered baseline from {:,} to {:,} records".format(archive_baseline_len, len(baseline_user_ids)))


def get_user_is_croatian(location):
    if location == '':
        return False
    
    cro_locations = ('croa', 'hrvat')
    
    if location.lower() in (loc.lower() for loc in locations):
        return True
    else:
        return any(cro_loc in location.lower() for cro_loc in cro_locations)


def get_user_clean_location(location):
    if location == '':
        return location
    
    location_lower = location.lower()
    location_names = ('republic of croatia', 'republika hrvatska', 'hrvatska', 'croatia', 'croacia', 'croatie')
    # accepted_chars = string.ascii_lowercase + 'čšćžđ'
    
    if re.search(r'\s+', location):
        location_lower = re.sub(r'\s+', ' ', location).strip().lower()
    
    for name in location_names:
        if name in location.lower():
            return 'Hrvatska'
    
    # for char in location.lower():
    #     if char not in accepted_chars + ' ':
    #         location_lower = location_lower.replace(char, ' ')
    
    if location_lower in ('', '🇭🇷'):
        location_lower = 'hrvatska'
    if location_lower == 'zg':
        location_lower = 'zagreb'
    return location_lower.title()


def transform(users_df):
    users_df['location'] = users_df['location'].fillna('').transform(lambda x: re.sub(r'\s+', ' ', x).strip())
    users_df['is_croatian'] = users_df['location'].transform(get_user_is_croatian)
    users_df['clean_location'] = users_df.loc[users_df['is_croatian'] == True, 'location'].transform(get_user_clean_location)
    return users_df.astype(USER_DTYPE)

# %%
SCRAPE_USER = lambda x: {
    'user_id':          x.get('id', x.get('user_id')),
    'user_id_str':      x.get('id_str', x.get('user_id_str')),
    'name':             x.get('name'),
    'screen_name':      x.get('screen_name'),
    'location':         x.get('location'),
    "profile_location": x.get('profile_location'),
    'derived':          x.get('derived'),
    'url':              x.get('url'),
    'description':      x.get('description'),
    'protected':        x.get('protected'),
    'verified':         x.get('verified'),
    'followers_count':  x.get('followers_count'),
    'friends_count':    x.get('friends_count'),
    'listed_count':     x.get('listed_count'),
    'favourites_count': x.get('favourites_count'),
    'statuses_count':   x.get('statuses_count'),
    'created_at':       x.get('created_at'),
    'profile_banner_url':      x.get('profile_banner_url'),
    'profile_image_url_https': x.get('profile_image_url_https'),
    'default_profile':         x.get('default_profile'),
    'default_profile_image':   x.get('default_profile_image'),
    'withheld_in_countries':   x.get('withheld_in_countries'),
    'withheld_scope':          x.get('withheld_scope'),
}


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
    'created_at':       'object',
    # 'profile_banner_url':      'string',
    # 'profile_image_url_https': 'string',
    # 'default_profile':         'object',
    # 'default_profile_image':   'string',
    # 'withheld_in_countries':   'object',
    # 'withheld_scope':          'object',

    ### Custom columns
    'is_croatian':      'bool',
    'clean_location':   'string'
}

# %%
def users():
    start_time = dt.datetime.now(settings.TZ_INFO)
    
    utils.mkdir(os.path.dirname(settings.CLEAN_USERS_CSV))

    logger.info("START - Cleaning Users ...")
    logger.info("Reading raw User json, this may take a while")
    
    all_users = []
    scrape_user_objs_dir = os.path.dirname(settings.SCRAPE_USER_OBJS_FN)
    for file_name in tqdm(os.listdir(scrape_user_objs_dir), desc='clean.users'):
        users = fileio.read_content(os.path.join(scrape_user_objs_dir, file_name), 'json')
        all_users += [SCRAPE_USER(user) for user in users]
        # all_users += users

    logger.info("Transforming User data, this may take a while")
    users_df = pd.DataFrame(all_users)
    if not users_df.empty:
        users_df = transform(users_df)
        users_df.to_csv(
            settings.CLEAN_USERS_CSV,
            index=False, 
            encoding='utf-8',
            quoting=csv.QUOTE_NONNUMERIC
        )
    
    logger.info("END - Done cleaning Users. Model saved: {}".format(settings.CLEAN_USERS_CSV))
    
    end_time = dt.datetime.now(settings.TZ_INFO)
    logger.info("Time elapsed: {} min".format(end_time - start_time))

# %%
if __name__ == '__main__':
    users()
    update_filtered_baseline()
