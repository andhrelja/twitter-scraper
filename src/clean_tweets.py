# %%
import os
import json
import pytz
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt

import settings


df = pd.DataFrame()
keywords = {
    'covid': [
      'alemka', 'markotic', 'markotić', 'beros', 'beroš', 'capak', 'hzjz',
      
      'antigensk', 'antimaskeri', 'antivakseri',
      
      'cijep', 'cijepiv', 'cijeplj', 'cijepljen', 'cjep', 'cjepiv', 'cjepljen',
      
      'booster doza', 'prva doza', 'druga doza', 'treca doza', 'treća doza',
      'astra zeneca', 'biontech', 'curevac', 'inovio', 'janssen', 'johnson', 
      'novavax', 'moderna', 'pfizer', 'vaxart',
      
      'sojevi koronavirusa', 'brazilski', 'britanski', 'ceski soj', 'delta', 
      'indijski', 'juznoafricki', 'južnoafrički', 'lambda', 
      'njujorski',  'njujorški', 'omikorn', 'omikron', 'novi soj', 'češki soj'
      
      'coron', 'corona', 'covid', 'covid-19', 'covid 19', 'koron', 'korona', 'kovid', 
      'ncov', 'mutira', 'mutaci', 'n95', 'sars-cov-2', 'sarscov2', 'sputnik',
      
      'inkubacij', 'ljekov', 'obolje', 'novozaražen', 'nuspoj', 'patoge', 'regeneron', 
      'medicin', 'infekc', 'dezinf', 'bolnic', 'dijagnost', 'doktor', 'epidem', 
      'respir', 'respirator', 'simpto', 'rt pcr', 'terapij', 'viro', 'virus',
      
      'slusaj struku', 'slušaj struku', 'propusnic', 'ostani doma', 'ostanimo doma', 'zaraž', 
      'festivala slobod',  'pcr', 'samoizola','samoizolacij', 'testira', 'zaraz',
      'distanc', 'izolac', 'karant', 'lockd', 'mask', 'festival slobod', 
      'ostanimo odgovorni', 'pandem', 'pandemij', 'stozer', 'stožer',
    ]
}

diacritics = {
    'č': 'c', 
    'ć': 'c', 
    'đ': 'd', 
    'š': 's', 
    'ž': 'z'
}

def load_output_tweets(tweets_path='tweets.csv'):
    global df
    
    if not os.path.exists(tweets_path):
        data = []
        for fn in os.listdir(settings.USERS_TWEETS_DIR):
            with open(os.path.join(settings.USERS_TWEETS_DIR, fn), 'r', encoding='utf-8') as f:
                content = json.load(f)
            for item in content:
                data.append({
                    'id': item.get('id'),
                    'user_id': item.get('user').get('id'),
                    'full_text': item.get('full_text'),
                    'created_at': item.get('created_at')
                })
                """
                'truncated': item.get('truncated'),               
                'place': item.get('place', {}).get('name'),
                'contributors': item.get('contributors'),
                'retweet_count': item.get('retweet_count'),
                'favorite_count': item.get('favorite_count'),
                'favorited': item.get('favorited'),
                'retweeted': item.get('retweeted'),
                'lang': item.get('lang'),
                
                # "{'type': 'Point', 'coordinates': [45.8, 16.0833]}"
                'latitude': item.get('geo', {}).get('coordinates', [None])[0],
                'longitude': item.get('geo', {}).get('coordinates', [None, None])[1],                    
                """

        df = pd.DataFrame(data)
        df['created_at'] = pd.to_datetime(df['created_at'], format='%a %b %d %H:%M:%S %z %Y')
    else:
        df = pd.read_csv('tweets.csv')
        df['created_at'] = pd.to_datetime(df['created_at'], format='%Y-%m-%d %H:%M:%S%z')

load_output_tweets()
df['week']  = df['created_at'].dt.strftime('%Y-%W')
df['month'] = df['created_at'].dt.strftime('%Y-%m')
df.info()

# %%
print("Total # of Tweets:", len(df))
print("# of Tweets in 2022:", len(df[df['created_at'] > dt.datetime(2022, 1, 1, 0, 0, 0, 0, pytz.UTC)]))

df = df[
    (df['created_at'] > dt.datetime(2021, 8, 1, 0, 0, 0, 0, pytz.UTC))
    & (df['created_at'] < dt.datetime(2022, 1, 31, 0, 0, 0, 0, pytz.UTC))
]
print("# of Tweets from 2021-08-01 - 2022-02-01:", len(df))

# %%
df['is_covid'] = df['full_text'].transform(lambda x: any(isinstance(x, str) and (tag in x.lower()
                                                or tag.replace(' ', '') in x.replace(' ', ''))
                                                for tag in keywords['covid']))
print("Non-Covid Tweets:", len(df[df['is_covid'] == False]))
print("Covid Tweets:", len(df[df['is_covid'] == True]))
print("# of Users who Tweet Covid topics:", len(df[df['is_covid'] == True]['user_id'].unique()))

df.groupby('is_covid').size().plot.bar()

# %%
fig, ax = plt.subplots(ncols=2, figsize=(14, 4))

df.groupby(['month', 'is_covid']).size().unstack('is_covid') \
    .plot.bar(
        title="Number of all Tweets by month", 
        rot=0,
        ax=ax[0],
        color=['#f8cecc', '#ffffff'],
        edgecolor='black'
    )
ax[0].legend(['C19', 'Regular'])
ax[0].set_xlabel(None)

df.groupby(['month', 'is_covid']).size().unstack('is_covid') \
    .plot.bar(
        title="Log number of all Tweets by month", 
        rot=0,
        ax=ax[1],
        color=['#f8cecc', '#ffffff'],
        edgecolor='black',
        logy=True
    )
ax[1].legend(['C19', 'Regular'])
ax[1].set_xlabel(None)

plt.show()


# %%
users_df = df.groupby('user_id').size().reset_index(name='counts')

print("Unique # of users:", len(users_df))
print("# of users with at least 5 Tweets:", len(users_df[users_df['counts'] > 5]))

# %%
users_df[users_df['counts'] > 5][['user_id', 'counts']].set_index('user_id') \
    .sort_values(by='counts', ascending=False).head(50).plot.bar(figsize=(30, 7))
users_df[users_df['counts'] > 5][['user_id', 'counts']].set_index('user_id') \
    .sort_values(by='counts', ascending=True).head(50).plot.bar(figsize=(30, 7))

# %%
gdf = df[['user_id', 'is_covid']].groupby(['user_id', 'is_covid']).size().reset_index(name='counts').set_index('user_id')
u_gdf = df.groupby('user_id').size().reset_index(name='counts').set_index('user_id')
gdf['num_tweets'] = u_gdf['counts']
gdf = gdf[(gdf['is_covid'] == True) & (gdf['num_tweets'] > 5)]
gdf['covid_pct'] = gdf['counts'] / gdf['num_tweets']
gdf['covid_related'] = gdf['covid_pct'].transform(lambda x: x > 0.5)

# %%
print("# of Users tweeting Covid related tweets:", len(gdf[gdf['covid_related'] == True]))

gdf[['covid_pct']].plot.hist(logy=True)
gdf[['covid_pct', 'covid_related']].sort_values(by='covid_pct', ascending=False).head(20)


# %%
df.to_csv('tweets.csv', encoding='utf-8')
gdf.to_csv('covid_related_tweets.csv', encoding='utf-8')
