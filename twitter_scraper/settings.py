import os
import json
import datetime as dt

now = dt.datetime.now()
folder_name = now.strftime('%Y-%m-%d')
# folder_name = '2022-07-27'

DEBUG = True if os.getenv('DEBUG', 'TRUE') == 'TRUE' else False

# ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
ROOT_DIR = os.getenv('TWITTER_SCRAPER_DIR', '/home/milky/infocov/twitter_scraper')

INPUT_DIR = os.path.join(ROOT_DIR, 'data', 'input')
OUTPUT_DIR = os.path.join(ROOT_DIR, 'data', 'output')
LOGS_DIR = os.path.join(ROOT_DIR, 'logs')
if DEBUG:
    INPUT_DIR = os.path.join(ROOT_DIR, 'debug', 'input')
    OUTPUT_DIR = os.path.join(ROOT_DIR, 'debug', 'output')
    LOGS_DIR = os.path.join(ROOT_DIR, 'debug', 'logs')

# Input
BASELINE_USER_IDS = os.path.join(INPUT_DIR, 'baseline-user-ids.json')
MISSING_USER_IDS = os.path.join(INPUT_DIR, 'missing-user-ids.json')
PROCESSED_USER_IDS = os.path.join(INPUT_DIR, 'processed-user-ids.json')
PROCESSED_USER_OBJS = os.path.join(INPUT_DIR, 'processed-user-objs.json')
# PROCESSED_USER_TWEETS = os.path.join(INPUT_DIR, 'processed-user-tweets.json')
STOP_WORDS_HRV = os.path.join(INPUT_DIR, 'stop-words-hrv.json')
STOP_WORDS_ENG = os.path.join(INPUT_DIR, 'stop-words-eng.json')
EMOJI_SENTIMENT_DATA = os.path.join(INPUT_DIR, 'Emoji_Sentiment_Data_v1.0.csv')

# Scrape
USER_IDS_DIR = os.path.join(OUTPUT_DIR, 'scrape', 'users', 'ids', folder_name)
USER_OBJS_DIR = os.path.join(OUTPUT_DIR, 'scrape', 'users', 'objs')
USER_TWEETS_DIR = os.path.join(OUTPUT_DIR, 'scrape', 'tweets')

# Clean
USERS_CSV = os.path.join(OUTPUT_DIR, 'clean', 'user', folder_name, 'users.csv')
TWEETS_CSV = os.path.join(OUTPUT_DIR, 'clean', 'tweet', folder_name, 'tweets.csv')

# Graph
NODES_CSV = os.path.join(OUTPUT_DIR, 'graph', folder_name, 'nodes.csv')
EDGES_MENTIONS_CSV = os.path.join(OUTPUT_DIR, 'graph', folder_name, 'edges-mentions.csv')
EDGES_RETWEETS_CSV = os.path.join(OUTPUT_DIR, 'graph', folder_name, 'edges-retweets.csv')
EDGES_FOLLOWERS_CSV = os.path.join(OUTPUT_DIR, 'graph', folder_name, 'edges-followers.csv')


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
