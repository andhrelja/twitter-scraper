# %%
import os
import json
import pytz
import pandas as pd
import datetime as dt

import settings


MIN_DATE = dt.datetime(2021, 8, 1, 0, 0, 0, 0, pytz.UTC)
MAX_DATE = dt.datetime(2022, 1, 31, 0, 0, 0, 0, pytz.UTC)

if not os.path.exists(os.path.join(settings.USERS_TWEETS_DIR, 'tweets.csv')):
    data = []
    for fn in os.listdir(settings.USERS_TWEETS_DIR):
        with open(os.path.join(settings.USERS_TWEETS_DIR, fn), 'r', encoding='utf-8') as f:
            content = json.load(f)
        for item in content:
            data.append({
                'id': item.get('id'),
                'user_id': int(fn.replace('.json', '')),
                'full_text': item.get('full_text'),
                'created_at': item.get('created_at')
            })

    df = pd.DataFrame(data)
    df['created_at'] = pd.to_datetime(df['created_at'], format='%a %b %d %H:%M:%S %z %Y') # 30s
    df['week']  = df['created_at'].dt.strftime('%Y-%W')
    df['month'] = df['created_at'].dt.strftime('%Y-%m')
else:
    df = pd.read_csv('2021_08-2022_02-tweets.csv')
    df['created_at'] = pd.to_datetime(df['created_at'], format='%Y-%m-%d %H:%M:%S%z') # 30s

df.info()

# %%
df = df[
    (df['created_at'] > MIN_DATE)
    & (df['created_at'] < MAX_DATE)
]

df['is_covid'] = df['full_text'].fillna('').transform(lambda x: any((tag in x.lower()
                                                     or tag.replace(' ', '') in x.replace(' ', ''))
                                                     for tag in settings.KEYWORDS['is_covid']))

# %%
users_df = df.groupby('user_id').agg(total_tweets=('user_id', 'size'))
users_df['covid_tweets']    = df[df['is_covid'] == True].groupby('user_id').size()
users_df['is_covid']        = users_df['covid_tweets'].transform(lambda x: x > 0)
users_df['covid_tweets']    = users_df['covid_tweets'].fillna(0)
users_df['covid_pct']       = users_df['covid_tweets'] / users_df['total_tweets']

print("[all] Unique # of users:", len(users_df))
print("[all] Unique # of users with at least 5 Tweets:", len(users_df[users_df['total_tweets'] > 5]))

print("[at least 1 covid tweet] Unique # of users:", len(users_df[users_df['is_covid'] == True]))
print("[at least 1 covid tweet] Unique # of users with at least 5 Tweets:", len(users_df[(users_df['is_covid'] == True) & (users_df['total_tweets'] > 5)]))

users_df.sort_values(by='covid_pct', ascending=False)#.to_csv(settings.NODES_CSV)

# %%
if __name__ == '__main__':
    graph_dir, _ = os.path.split(settings.NODES_CSV)
    if not os.path.exists(graph_dir):
        os.mkdir(graph_dir)