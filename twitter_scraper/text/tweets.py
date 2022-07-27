# %%
from urllib.parse import urlparse
from langdetect import detect

from nltk.stem import PorterStemmer
import gensim
import pandas as pd
import re

from twitter_scraper import settings
from twitter_scraper.utils import fileio
from twitter_scraper.clean.tweets import TWEET_DTYPE
from twitter_scraper.text.stemmer import croatian_stemmer

stop_words_eng = fileio.read_content(settings.STOP_WORDS_ENG, 'json')
stop_words_hrv = fileio.read_content(settings.STOP_WORDS_HRV, 'json')

ps = PorterStemmer()
tweets_df = pd.read_csv(settings.TWEETS_CSV, dtype=TWEET_DTYPE)

def is_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

# %%
def replace_all_mentions(text):
    for mention in re.findall('@[A-Za-z0-9-_]+', text):
        text = text.replace(mention, '')
    return text.strip()

def detect_language(text):
    try:
        lang = detect(text)
    except Exception:
        lang = 'zxx'
    return lang

def get_stemmed_tweets_df(tweets_df):
    tweets_df['full_text_processed']  = tweets_df['full_text'].transform(lambda x: ' '.join(y for y in x.split() if not is_url(y)))
    tweets_df['full_text_processed']  = tweets_df['full_text_processed'].fillna('None')
    tweets_df['full_text_processed']  = tweets_df['full_text_processed'].transform(replace_all_mentions)
    tweets_df['full_text_processed']  = tweets_df['full_text_processed'].str.replace('RT : ', '')
    tweets_df['full_text_processed']  = tweets_df['full_text_processed'].transform(lambda x: 'None' if x.strip() == '' else x)
    tweets_df['language']   = tweets_df['full_text_processed'].transform(detect_language)
    # tweets_df['full_text_processed']  = tweets_df['full_text_processed'].transform(lambda x: re.sub('[,\.:;!?]', '', x))
    tweets_df['full_text_processed']  = tweets_df['full_text_processed'].transform(gensim.utils.simple_preprocess)
    tweets_df['full_text_processed']  = tweets_df.apply(lambda x: [word for word in x.full_text_processed if (x.lang != 'hr' and word not in stop_words_eng) or (x.lang == 'hr' and word not in stop_words_hrv)], axis=0)
    tweets_df['lang']       = tweets_df.apply(lambda x: x.language if x.lang == 'und' else x.lang, axis=1)
    tweets_df['stemmed']    = tweets_df.apply(lambda x: croatian_stemmer.croatian_stemmer(x.full_text_processed) if x.lang == 'hr' else " ".join([ps.stem(word) for word in x.full_text_processed]), axis=1)
    return tweets_df
    
# %%
def tweets():
    global tweets_df
    tweets_df = get_stemmed_tweets_df(tweets_df)
    tweets_df.to_csv('tweets-text.csv')
    
# %%
if __name__ == '__main__':
    tweets()