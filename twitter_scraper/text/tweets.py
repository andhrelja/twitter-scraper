# %%
import langid
import gensim
import stanza
import classla
# import emoji
import re
import os
import pickle
import pandas as pd

import pyLDAvis
import pyLDAvis.gensim_models as gensimvis

from twitter_scraper import settings
from twitter_scraper import utils
from twitter_scraper.utils import fileio
from twitter_scraper.clean.tweets import TWEET_DTYPE


logger = utils.get_logger(__file__)

stop_words_eng = fileio.read_content(settings.STOP_WORDS_ENG, 'json')
stop_words_hrv = fileio.read_content(settings.STOP_WORDS_HRV, 'json')
# Because of the way our dataset is limited, we are assuming
# we can allow to concatenate english and croatian stop words
stop_words = stop_words_eng + stop_words_hrv 

nlps = {
    'en': stanza.Pipeline('en', use_gpu=False, logging_level='ERROR'),
    'hr': classla.Pipeline('hr', use_gpu=False, logging_level='ERROR'),
    'sr': classla.Pipeline('sr', use_gpu=False, logging_level='ERROR'),
    'sl': classla.Pipeline('sl', use_gpu=False, logging_level='ERROR')
}
nlps['bs'] = nlps['hr']

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
    return text

def get_stemmed_text(text, lang=None):
    # text = re.sub(URL_REGEX, '', text)
    if text == '':
        return []
    
    if lang is None:
        lang = detect_language(text)
    
    text = gensim.utils.simple_preprocess(text)
    text = [word.lower() for word in text if word.lower() not in stop_words]
    
    if not text:
        return text
    
    if lang in ('hr', 'bs', 'sr', 'sl'):
        nlp = nlps[lang]
    else:
        nlp = nlps['en']
        
    doc = nlp(" ".join(text))
    text = [word.lemma for sentence in doc.sentences for word in sentence.words]
    return text

def get_stemmed_tweets_df(tweets_df, text_col_name):
    _text_col_name = "{}_transform".format(text_col_name)
    def get_lemmatized_text(row):
        if row['langid'] in ('hr', 'bs', 'sr', 'sl'):
            nlp = nlps[row['langid']]
        else:
            nlp = nlps['en']
            
        if not row[_text_col_name]: 
            return []
        
        doc = nlp(" ".join(row[_text_col_name]))
        return [word.lemma for sentence in doc.sentences for word in sentence.words]
    
    tweets_df[_text_col_name]  = tweets_df[text_col_name].fillna('')
    tweets_df[_text_col_name]  = tweets_df[_text_col_name].transform(lambda x: re.sub(URL_REGEX, '', x))
    # tweets_df[_text_col_name]  = tweets_df[_text_col_name].transform(lambda x: re.sub(SYMBOLS_REGEX, '', x))
    tweets_df[_text_col_name]  = tweets_df[_text_col_name].transform(lambda x: re.sub(MENTIONS_REGEX, '', x))
    tweets_df[_text_col_name]  = tweets_df[_text_col_name].str.replace('RT', '')
    tweets_df[_text_col_name]  = tweets_df[_text_col_name].str.strip()
    
    logger.info("Running gensim.utils.simple_preprocess")
    tweets_df[_text_col_name]  = tweets_df[_text_col_name].transform(gensim.utils.simple_preprocess)

    logger.info("Removing stop words")
    tweets_df[_text_col_name]  = tweets_df.apply(lambda x: [word for word in x.full_text_processed if word not in stop_words], axis=1)
    logger.info("Running (classla.Pipeline, stanza.Pipeline)")
    tweets_df['stemmed'] = tweets_df.apply(get_lemmatized_text, axis=1)
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
def tweets(tweets_csv=settings.TWEETS_CSV, text_col_name='full_text'):    
    utils.mkdir(os.path.dirname(settings.TWEETS_TEXT_CSV))
    
    logger.info("Reading tweets CSV")
    tweets_df = pd.read_csv(tweets_csv, dtype=TWEET_DTYPE)
    logger.info("Starting text transformations")
    tweets_df = get_stemmed_tweets_df(tweets_df, text_col_name)
    tweets_df.to_csv(settings.TWEETS_TEXT_CSV, index=False)
    
# %%
if __name__ == '__main__':
    tweets(
        tweets_csv=settings.TWEETS_CSV
    )