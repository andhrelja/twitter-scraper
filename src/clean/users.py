# %%
import re
import os
import string
import pandas as pd
import datetime as dt

import fileio
import settings

USER_OBJS_CSV = os.path.join(settings.USER_OBJS_DIR, 'user-objs.csv')
LOCATIONS_JSON = os.path.join(settings.ROOT_DIR, 'input', 'locations.json')

locations = pd.read_json(LOCATIONS_JSON)[0]

INPUT = {
    'user_id'        : pd.Int64Dtype(),
    'protected'      : pd.BooleanDtype(),
    'screen_name'    : pd.StringDtype(),
    'location'       : pd.StringDtype(),
    'name'           : pd.StringDtype(),
    'description'    : pd.StringDtype(),
    'verified'       : pd.BooleanDtype(),
    'created_at'     : pd.StringDtype(),
    'statuses_count' : pd.Int64Dtype(),
    'friends_count'  : pd.Int64Dtype(),
    'followers_count': pd.Int64Dtype(),
}

OUTPUT = {
    'user_id'        : pd.Int64Dtype(),
    'protected'      : pd.BooleanDtype(),
    'screen_name'    : pd.StringDtype(),
    'location'       : pd.StringDtype(),
    'created_at'     : dt.datetime,
}

user_df = pd.read_csv(USER_OBJS_CSV, dtype=INPUT)
#user_df = pd.read_csv('C:\\Users\\AndreaHrelja\\Documents\\Faks\\twitter_scraper\\output\\users\\objs\\2022-02-03\\user-objs.csv')
user_df['created_at'] = pd.to_datetime(user_df['created_at'], format='%a %b %d %H:%M:%S %z %Y') # 30s
user_df.info()

# %%
accepted_chars = string.ascii_lowercase + 'čšćžđ'
diacritics = {
    'č': 'c', 
    'ć': 'c', 
    'đ': 'd', 
    'š': 's', 
    'ž': 'z'
}


def clean_location(location):
    if location == '':
        return location
    
    new_location = location
    location_names = ('hrvatska', 'croatia', 'croacia', 'croatie', 'republic of croatia', 'republika hrvatska')
    
    if re.search(r'[ ]+', location):
        new_location = new_location.replace(re.search(r'[ ]+', location).group(), ' ').strip()
    
    for name in location_names:
        if new_location.lower() == name:
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
    if location == '':
        return False

    for old, new in diacritics.items():
        if old in location:
            loc = loc.replace(old, new)
                
    global locations
    for loc in locations:        
        if location in loc or location.lower() in loc.lower():
            return True
        
        _clean_location = clean_location(location).lower()
        _clean_loc = clean_location(loc).lower()
        if (_clean_location in _clean_loc
            or _clean_loc in _clean_location):
            return True

        if (loc.replace(' ', '') in location.replace(' ', '')
            or _clean_location.replace(' ', '') in _clean_loc.replace(' ', '')
            or location.replace(' ', '') in loc.replace(' ', '')
            or _clean_loc.replace(' ', '') in _clean_location.replace(' ', '')):
            return True
    
    return False

user_df['clean_location'] = user_df['location'].fillna('').transform(clean_location)
user_df['is_croatian']   = user_df['location'].fillna('').transform(is_croatian)

# %%
output_df = user_df[
    (user_df['is_croatian'] == True)
    & (user_df['protected'] == False)
    & (user_df['statuses_count'] > 10)
    & (user_df['friends_count'] > 10)
    & (user_df['friends_count'] < 5000)
    & (user_df['followers_count'] > 10)
    #& (user_df['followers_count'] < 5000)
].astype(OUTPUT).sort_values(by='followers_count')

#output_df.to_csv(os.path.join(settings.USER_OBJS_DIR, 'clean-user-objs.csv'), encoding='utf-8', index=False)
#output_df.user_id.to_json('../../output/new_baseline-user-ids.json', orient='records')
output_df.head()
# %%

def generate_edges_df(output_df):
    not_found = 0
    users_data = []
    total_users = len(output_df.user_id.unique())
    
    for user_id in output_df.user_id.unique():
        user_path = os.path.join(settings.USER_IDS_DIR, '{}.json'.format(user_id))
        if os.path.exists(user_path):
            user = fileio.read_content(user_path, 'json')
            for follower in user.get('followers'):
                users_data.append({
                    'source': follower,
                    'target': str(user_id)
                })
        else:
            not_found += 1
    
    print("Found {}/{} users".format(total_users-not_found, not_found))
    return pd.DataFrame(users_data)

edges_df = generate_edges_df(output_df)
edges_df#.to_csv(settings.EDGES_CSV, index=False)

# %%

if __name__ == '__main__':
    graph_dir, _ = os.path.split(settings.EDGES_CSV)
    if not os.path.exists(graph_dir):
        os.mkdir(graph_dir)