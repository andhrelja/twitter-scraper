import os
import json
import datetime as dt

TZ_INFO = dt.timezone.utc
now = dt.datetime.now(TZ_INFO)
folder_name = now.strftime('%Y-%m-%d')
folder_name = os.getenv('FOLDER_NAME', '2022-11-20')
# folder_name = '2022-11-01'

DEBUG = os.getenv('DEBUG', 'true') == 'true'
TEXT_USE_GPU = os.getenv('USE_GPU', 'true') == 'true'
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

if DEBUG:
    ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
else:
    ROOT_DIR = os.getenv('TWITTER_SCRAPER_DATA_DIR', '/srv/milky/twitter_scraper')

INPUT_DIR     = os.path.join(ROOT_DIR, 'data', 'input')
OUTPUT_DIR    = os.path.join(ROOT_DIR, 'data', 'output')
LOGS_DIR      = os.path.join(ROOT_DIR, 'logs')

# Input
## Lookups
LOOKUPS_DIR   = os.path.join(INPUT_DIR, 'lookups')
## Locations
LOCATIONS_HR  = os.path.join(INPUT_DIR, 'locations', 'hr.json')
## Stop words
STOP_WORDS_HR = os.path.join(INPUT_DIR, 'stop_words', 'hr.json')
STOP_WORDS_EN = os.path.join(INPUT_DIR, 'stop_words', 'en.json')

## Users
BASELINE_USER_IDS   = os.path.join(INPUT_DIR, 'baseline-user-ids.json')
MISSING_USER_IDS    = os.path.join(INPUT_DIR, 'missing-user-ids.json')
PROCESSED_USER_IDS  = os.path.join(INPUT_DIR, 'processed-user-ids.json')
PROCESSED_USER_OBJS = os.path.join(INPUT_DIR, 'processed-user-objs.json')
MAX_TWEET_IDS       = os.path.join(INPUT_DIR, 'max-tweet-ids.json')

## Static
LOCATIONS_HRV       = os.path.join(INPUT_DIR, 'locations', 'hr.json')
STOP_WORDS_HRV      = os.path.join(INPUT_DIR, 'stop_words', 'hr.json')
STOP_WORDS_ENG      = os.path.join(INPUT_DIR, 'stop_words', 'en.json')
SENTIMENT_LOOKUP    = os.path.join(LOOKUPS_DIR, 'sentiment-lookup.csv')
LEMMA_LOOKUP        = os.path.join(LOOKUPS_DIR, 'lemma-lookup.csv')

# Output

# Directories
## Scrape
SCRAPE_USER_DIR     = os.path.join(OUTPUT_DIR, 'scrape', 'users')
SCRAPE_TWEETS_DIR   = os.path.join(OUTPUT_DIR, 'scrape', 'tweets')

## Clean
CLEAN_USERS_DIR     = os.path.join(OUTPUT_DIR, 'clean', 'users')
CLEAN_TWEETS_DIR    = os.path.join(OUTPUT_DIR, 'clean', 'tweets')

## Graph
GRAPH_DIR           = os.path.join(OUTPUT_DIR, 'graph')

# Directories
## Scrape
SCRAPE_USER_OBJS_FN = os.path.join(SCRAPE_USER_DIR, 'objs', folder_name, 'users.json')
SCRAPE_USER_IDS_FN  = os.path.join(SCRAPE_USER_DIR, 'ids', folder_name, '{user_id}.json')
SCRAPE_TWEETS_FN    = os.path.join(SCRAPE_TWEETS_DIR, folder_name, '{user_id}.json')

## Clean
CLEAN_USERS_CSV     = os.path.join(CLEAN_USERS_DIR, folder_name, 'users.csv')
CLEAN_TWEETS_CSV    = os.path.join(CLEAN_TWEETS_DIR, folder_name, 'tweets.csv')

## Graph 
NODES_CSV           = os.path.join(OUTPUT_DIR, 'graph', folder_name, 'nodes.csv')
EDGES_MENTIONS_CSV  = os.path.join(OUTPUT_DIR, 'graph', folder_name, 'edges-mentions.csv')
EDGES_RETWEETS_CSV  = os.path.join(OUTPUT_DIR, 'graph', folder_name, 'edges-retweets.csv')
EDGES_FOLLOWERS_CSV = os.path.join(OUTPUT_DIR, 'graph', folder_name, 'edges-followers.csv')

## Text
TEXT_TWEETS_CSV = os.path.join(OUTPUT_DIR, 'text', folder_name, 'tweets.csv')

KEYWORDS = {
    'is_covid': [
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
      'respir', 'respirator', 'simpto', 'rt pcr', 'terapij', 'virus', # 'viro',
      
      'slusaj struku', 'slušaj struku', 'propusnic', 'ostani doma', 'ostanimo doma', 'zaraž', 
      'festivala slobod',  'pcr', 'samoizola','samoizolacij', 'zaraz', #'testira',
      'distanc', 'izolac', 'karant', 'lockd', 'mask', 'festival slobod', 
      'ostanimo odgovorni', 'pandem', 'pandemij', 'stozer', 'stožer',
    ]
}

with open(os.path.join(ROOT_DIR, 'twitter-credentials.json'), 'r', encoding='utf-8') as f:
    connections = json.load(f)

# with open(os.path.join(INPUT_DIR, 'latest-load.json'), 'r', encoding='utf-8') as f:
#     latest_load_json = json.load(f)
