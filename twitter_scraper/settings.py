import os
import datetime as dt

now = dt.datetime.now()
folder_name = now.strftime('%Y-%m-%d')
folder_name = '2022-07-21'

DEBUG = False

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))

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
PROCESSED_USER_TWEETS = os.path.join(INPUT_DIR, 'processed-user-tweets.json')
STOP_WORDS_HRV = os.path.join(INPUT_DIR, 'stop_words_hrv.json')
STOP_WORDS_ENG = os.path.join(INPUT_DIR, 'stop_words_eng.json')


# Scrape
USER_IDS_DIR = os.path.join(OUTPUT_DIR, 'scrape', 'users', 'ids')
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

connections = {
    'Carlos': {
        'consumer_key': 'r1tcZ5XPtMLzBhwNEZjhHb3vV',
        'consumer_secret': '7cGo82YQGOYGi3iJ1LJ9YeMP4GA6paIe2kabLLeicjMrUUhXxs',
        'access_key': '166318369-AhoqOVupAsjj0EnrVtHY6Pg3izqremykKLvZpjBV',
        'access_secret': 'kRCuZRn0j0Iowqd7VBCTQRgYuM5ZpwAc6ViEzmwJtFPcS',
    },
    'IC': {
        'consumer_key': 'D1cFTRrLpIpJT136NfBo2A0u9' ,
        'consumer_secret': '3n6YDxzye30OahadlibPcZoh8H6yWB9FQ2x4JfNo4UR0k7m5xH',
        'access_key': '1169317946033922048-gnnApT1ZUfmoNeaTOykz9yM2FRsiWL',
        'access_secret': 'fN6l6WCjapzwWAW8dU0xiOFExhzeVOHnhmCJg3wwpSopv',
    },
    'IC2': {
        'consumer_key': 'm3NrMZ7PB4WVrDYAekQEr7mug',
        'consumer_secret': 'Pjl6UWbaye7PrP697nv5YHKngwcqnhVMAXdAtRCEJ02ppVXlVj',
        'access_key': '1316409694760689666-YSi25euJltCKcDWI1XeM24LUiK4uG5',
        'access_secret': 'cb3MG4RJeFkwt2FmHhgIH0V7OfijuN3MxXCcA1P3ntKlP',
    },
    
    'andhrelja': {# AAAAAAAAAAAAAAAAAAAAABQAYwEAAAAAtdo8GPg%2BU8LkZch6B6kvkZAxTlE%3DxinBDLcs1zGPI4OEytAVCzYucBTAf8V4q0KBjEGWHtDqgUKAMn
        'consumer_key': 'Bf4MSXC7sM3f4uzLOTIJTwFUR' ,
        'consumer_secret': 'EEEW1hrODIsC4b9aSSA8yu0egSTap9TBr2DuuIMbkcLTEQkwSN',
        'access_key': '146153494-v4l1gPVW9dkYTIMPTSKgrF8Jg7PHnxQj5dYExVpU',
        'access_secret': 'xn9SuKIEgrkFzyc6pb3QakIWx9rJP1gHoj64JwG7gBPtW',
    },
    'BioOrNotToBio': {# AAAAAAAAAAAAAAAAAAAAAIMFYwEAAAAAXfxTFhUw%2F3DpiNLBRXxGjkTslFI%3DyT7oCGI2H4Ovhikjy9zUQB2TGd90jc76fO9Avatz4uJV9o4f6w
        'consumer_key': 'KfvPOv5gzd4Wstehms12KwHHT' ,
        'consumer_secret': '0JCkSUP7VbjlK7hBBfxhxpzjSkfQfwuRHK4idEqOfZav8loAUm',
        'access_key': '1488520803033534466-qIqsR9jQ4kyn3ZC0ERuihpuBvFbQUq',
        'access_secret': 'mFfop6ca17HgOpRbMFqoSApOtkMlT2ITEVGX7AqSV0f8n',
    },
    'KinderGartenRi': {# AAAAAAAAAAAAAAAAAAAAALQFYwEAAAAAK6xHNFNjs02d%2FgACwqjJxCcssZE%3DXOduVoQTyfqV0ycSXWtPTxKoWAGZtIKHGQVi07dMUC5DNszNj6
        'consumer_key': 'I7CJiw0SOzXaW8D28oYLYbDVd' ,
        'consumer_secret': 'WrTU9mm4QO1RFriMc4XCWhEVjf9XRCETcHPxZvv7I89wgjfMgq',
        'access_key': '1488523272891375621-y8ItLVJkeUmEZh4ZtUsWTgJ0ArRxAj',
        'access_secret': 'M4NzuVKkcFxXbNkoyxEmChQ9t4FLSkryTEORcuE8lsHOp',
    },
    'FgnkbD': {# AAAAAAAAAAAAAAAAAAAAANQiYwEAAAAACJCxyjSgktQSs4B0RJIE2fa%2B%2Btk%3Dl5SkH9lvvlIprxjEdX1X4zLuPT0OtvjOktaSu17W5Yqz6yw1xP
        'consumer_key': 'kS6qipbXACkVEivDCiH57tPyh' ,
        'consumer_secret': 'Mt0IfbbHE1CBSWa6JwYJ6PS4NGCTlyWCNDf0HK1Bd3o6VwTgy2',
        'access_key': '1488806279443267584-szOY2s3WLLLDRuxJGPo7FvuEJRAn7b',
        'access_secret': '9UFSArk8Hi7KE0sPN19P7a8H9WjfVP8BZ9mzNVVln9kjA',   
    },
    'SladoledC': {# AAAAAAAAAAAAAAAAAAAAACQjYwEAAAAAK4JlqtZKXs5aCgWOHtgLlTq2LCc%3D3gyOi7NOYN5ttmbVHTiy9PP5I9aSzJ7I09RnZL1XipPyXQ1oWQ
        'consumer_key': 'HYp0liFrU4PE7fcvtEU6Xb22I' ,
        'consumer_secret': 'tlC9v69Rev2aBHq2HfoAnFw3LOrlj9S4GGJupSQ4UVJvJxsotC',
        'access_key': '1488632889143144456-o410S6RSUtsdQMCqevJrEEa9TbfEjD',
        'access_secret': 'JyHqhzpRKQ1JcYrdJk82n1smy4wihQnBpJAZpidPy9Bvc', 
    },
    'PScrapic': {# AAAAAAAAAAAAAAAAAAAAACQjYwEAAAAAK4JlqtZKXs5aCgWOHtgLlTq2LCc%3D3gyOi7NOYN5ttmbVHTiy9PP5I9aSzJ7I09RnZL1XipPyXQ1oWQ
        'consumer_key': 'DEkHAdYHrzKlUASVe8jzvzg3d' ,
        'consumer_secret': 'VBavpBz2OhvY6IT01sfc9huZsTSULHN7vWFLMYnqlTG3v82Phe',
        'access_key': '1489370296180224004-yomr0TnLaUJoiy4FVl7vAupx0VHqXt',
        'access_secret': '8k6Xrvecrflogjxzo8AOXdRo5usUY2J3siSCSrArIBeeL', 
    },
}
