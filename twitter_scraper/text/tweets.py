# %%
import langid
import gensim
# import emoji
import re
import os
import pickle
import pandas as pd

import pyLDAvis
import pyLDAvis.gensim_models as gensimvis

from nltk.stem import WordNetLemmatizer

from twitter_scraper import settings
from twitter_scraper import utils
from twitter_scraper.utils import fileio
from twitter_scraper.clean.tweets import TWEET_DTYPE
from twitter_scraper.text.stemmer import croatian_stemmer


logger = utils.get_logger(__file__)

stop_words_eng = fileio.read_content(settings.STOP_WORDS_ENG, 'json')
stop_words_hrv = fileio.read_content(settings.STOP_WORDS_HRV, 'json')

lemmatizer = WordNetLemmatizer()
tweets_df = pd.read_csv(settings.TWEETS_CSV, dtype=TWEET_DTYPE)
emoji_sentiment_df = pd.read_csv(settings.EMOJI_SENTIMENT_DATA)

URL_REGEX = r'https?:\/\/[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)'
# SYMBOLS_REGEX = r'[,\.:;!?]'
MENTIONS_REGEX = r'@[A-Za-z0-9-_]+'
TRANSFORM = lambda x: {

}

# %%
def detect_language(text):
    if text is None or text == '':
        return 'zxx'
    try:
        lang, _ = langid.classify(text)
    except Exception:
        lang = 'zxx'
    return lang

def clean_twitter_text(text):
    text = re.sub(URL_REGEX, '', text)
    text = re.sub(MENTIONS_REGEX, '', text)
    text = text.replace('RT', '').strip()
    if text.startswith(':'): text = text[1:]
    return text.strip()

def get_stemmed_text(text, lang=None):
    if lang is None:
        lang = detect_language(text)
    
    if lang == 'en':
        stop_words = fileio.read_content(settings.STOP_WORDS_ENG, 'json')
    elif lang in ('hr', 'bs', 'sr', 'sl'):
        stop_words = fileio.read_content(settings.STOP_WORDS_HRV, 'json')
    else:
        stop_words = []
    
    if text == '':
        return ''

    text = gensim.utils.simple_preprocess(text)
    text = [word.lower() for word in text if word.lower() not in stop_words]
    
    if lang in ('hr', 'bs', 'sr', 'sl'):
        text = [croatian_stemmer.croatian_stemmer(word) for word in text]
    else:
        text = [lemmatizer.lemmatize(word) for word in text]
    return text


def get_stemmed_tweets_df(tweets_df):
    tweets_df['full_text_processed']  = tweets_df['full_text'].fillna('None').replace('', 'None')
    tweets_df['full_text_processed']  = tweets_df['full_text_processed'].transform(lambda x: 'None' if x == '' else x)
    tweets_df['full_text_processed']  = tweets_df['full_text_processed'].transform(lambda x: re.sub(URL_REGEX, '', x))
    # tweets_df['full_text_processed']  = tweets_df['full_text_processed'].transform(lambda x: re.sub(SYMBOLS_REGEX, '', x))
    tweets_df['full_text_processed']  = tweets_df['full_text_processed'].transform(lambda x: re.sub(MENTIONS_REGEX, '', x))
    tweets_df['full_text_processed']  = tweets_df['full_text_processed'].str.replace('RT', '')
    tweets_df['full_text_processed']  = tweets_df['full_text_processed'].str.strip()
    
    logger.info("Running langdetect.detect_language")
    # tweets_df['language']   = tweets_df['full_text_processed'].transform(lambda x: x.lang if x.lang == 'en' else detect_language(x))
    tweets_df['language']   = tweets_df['full_text_processed'].transform(detect_language)

    logger.info("Running gensim.utils.simple_preprocess")
    tweets_df['full_text_processed']  = tweets_df['full_text_processed'].transform(gensim.utils.simple_preprocess)

    logger.info("Removing stop words")
    tweets_df['full_text_processed']  = tweets_df.apply(lambda x: [word for word in x.full_text_processed if (x.language != 'hr' and word not in stop_words_eng) or (x.language == 'hr' and word not in stop_words_hrv)], axis=1)
    tweets_df['stemmed']    = tweets_df.apply(lambda x: croatian_stemmer.croatian_stemmer(x.full_text_processed) if x.language == 'hr' else [lemmatizer.lemmatize(word) for word in x.full_text_processed], axis=1)
    return tweets_df


def get_corpus_tweets_df(tweets_df):
    id2word = gensim.corpora.Dictionary(tweets_df['stemmed'])
    corpus = [id2word.doc2bow(text) for text in tweets_df['stemmed']]
    lda_model = gensim.models.LdaMulticore(
        corpus=corpus,
        id2word=id2word,
        num_topics=10
    )
    doc_lda = lda_model[corpus]
    # tweets_df.loc[6].full_text
    # doc_lda[6]
    # lda_model.print_topic(6)

    # Visualize the topics
    pyLDAvis.enable_notebook()
    LDAvis_data_filepath = os.path.join(settings.OUTPUT_DIR, 'LDAvis/ldavis_prepared')
    # # this is a bit time consuming - make the if statement True
    # # if you want to execute visualization prep yourself
    if 1 == 1:
        LDAvis_prepared = gensimvis.prepare(lda_model, corpus, id2word, mds='mmds')
        with open(LDAvis_data_filepath, 'wb') as f:
            pickle.dump(LDAvis_prepared, f)
    # load the pre-prepared pyLDAvis data from disk
    with open(LDAvis_data_filepath, 'rb') as f:
        LDAvis_prepared = pickle.load(f)
    pyLDAvis.save_html(LDAvis_prepared, os.path.join(settings.OUTPUT_DIR, 'LDAvis/ldavis_prepared.html'))

    
# %%
def tweets():
    global tweets_df
    tweets_df = get_stemmed_tweets_df(tweets_df)
    tweets_df.to_csv('tweets-text.csv')
    
# %%
if __name__ == '__main__':
    tweets()