# %%
# %env CUDA_VISIBLE_DEVICES=2
# %env MODIN_ENGINE=dask
import gensim
import stanza
import classla
# import demoji
import csv
import re
import os
import pickle
# import modin.pandas as pd
import pandas as pd
from collections import defaultdict

import pyLDAvis
import pyLDAvis.gensim_models as gensimvis

from twitter_scraper import settings
from twitter_scraper import utils
from twitter_scraper.utils import fileio
from twitter_scraper.clean.tweets import TWEET_DTYPE


available_stanza_languages = stanza.resources.common.list_available_languages()
classla_supported_languages = ['hr', 'sl', 'sr', 'bg', 'mk']
stanza_supported_languages = set(available_stanza_languages).difference(classla_supported_languages)

USE_STANZA_LANGUAGES = ['en',]
USE_CLASSLA_LANGUAGES = ['hr', 'sl', 'sr', 'bs']

logger = utils.get_logger(__file__)

stop_words_eng = fileio.read_content(settings.STOP_WORDS_ENG, 'json')
stop_words_hrv = fileio.read_content(settings.STOP_WORDS_HRV, 'json')
# Because of the way our dataset is limited, we are assuming
# we can allow to concatenate english and croatian stop words
stop_words = stop_words_eng + stop_words_hrv 

def default_nlp():
    return stanza.Pipeline(
        lang='en', 
        use_gpu=settings.TEXT_USE_GPU, 
        logging_level='ERROR',
        processors='tokenize,pos,lemma'
    )

nlps = defaultdict(default_nlp)
sentiment_lookup_df = pd.read_csv(settings.SENTIMENT_LOOKUP)

URL_REGEX = r'https?:\/\/[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)'
MENTIONS_REGEX = r'@[A-Za-z0-9-_]+'


# %%
def setup_global_nlps():
    global nlps
    
    for stanza_lang in filter(lambda x: x in USE_STANZA_LANGUAGES, stanza_supported_languages):
        nlps[stanza_lang] = stanza.Pipeline(
            lang=stanza_lang, 
            use_gpu=settings.TEXT_USE_GPU, 
            logging_level='ERROR',
            processors='tokenize,pos,lemma'
        )
    
    for classla_lang in filter(lambda x: x in USE_CLASSLA_LANGUAGES, classla_supported_languages):
        nlps[classla_lang] = classla.Pipeline(
            lang=classla_lang, 
            use_gpu=settings.TEXT_USE_GPU, 
            logging_level='ERROR',
            processors='tokenize,pos,lemma'
        )
    
    nlps['bs'] = nlps['hr']


def get_text_dt(tweets_df, start_date=None, end_date=None):
    # start_date = '2022-11-09T00:00:00+00:00'
    # end_date = '2022-11-10T00:00:00+00:00'
    if start_date and end_date:
        import datetime as dt
        start_date = dt.datetime.fromisoformat(start_date)
        end_date = dt.datetime.fromisoformat(end_date)
        tweets_df = tweets_df[
            (tweets_df['created_at'] > start_date) 
            & (tweets_df['created_at'] < end_date)
        ]
        
    def apply_nlp(row, text_col_name='text', keep_upos=('NOUN', 'PROPN', 'ADJ')):
        if len(row[text_col_name]) > 0:
            nlp = nlps[row['lang']]
            doc = nlp(" ".join(row[text_col_name]))
            return [word.lemma
                    for sentence in doc.sentences
                    for word in sentence.words
                    if word.upos in keep_upos]
        else:
            return []

    
    text_df = tweets_df[tweets_df['lang'].isin(USE_STANZA_LANGUAGES + USE_CLASSLA_LANGUAGES)].copy()
    text_df['text'] = text_df['full_text'].transform(lambda x: re.sub(URL_REGEX, '', x))
    text_df['text'] = text_df['text'].transform(lambda x: re.sub(MENTIONS_REGEX, '', x))
    # text_df['emoji'] = text_df['text'].transform(demoji.findall_list, desc=False)
    
    logger.info("Running gensim.utils.simple_preprocess ...")
    text_df['text'] = text_df['text'].transform(gensim.utils.simple_preprocess)
    
    logger.info("Running stop_words filtering ...")
    text_df['text'] = text_df['text'].transform(
        lambda text: [word for word in text if word not in stop_words]
    )
    
    logger.info("Running lemmatization  ...")
    text_df['lemmatized'] = text_df.apply(apply_nlp, axis=1)
    
    texts = [list(filter(None, x)) for x in text_df['lemmatized']]
    texts = list(filter(lambda x: x != [], texts))
    
    logger.info("Running gensim bigrams ...")
    bigrams = gensim.models.Phrases(sentences=texts, min_count=50, threshold=50)
    bigram_model = gensim.models.phrases.Phraser(bigrams)

    logger.info("Running gensim trigrams ...")
    trigrams = gensim.models.Phrases(sentences=bigram_model[texts], min_count=20, threshold=100)
    # bitri_grams = trigrams[bigram_model[texts]]
    
    
    logger.info("Applying Phrases model ...")
    text_df['word_grams'] = text_df['lemmatized'].transform(lambda x: trigrams[bigram_model[x]] if len(x) > 0 else [])
    return text_df

def _get_adhoc_tweets_df(tweets_df):
    
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
def tweets(adhoc=True):
    TEXT_TWEETS_CSV = settings.TEXT_TWEETS_CSV
    if adhoc:
        TEXT_TWEETS_CSV = settings.TEXT_TWEETS_CSV.replace(settings.folder_name, 'adhoc')
    
    logger.info("Setting up NLPs (stanza, classla) ...")  
    setup_global_nlps()
    utils.mkdir(os.path.dirname(TEXT_TWEETS_CSV))
    
    logger.info("Reading tweets CSV")
    tweets_df = pd.read_csv(
        settings.CLEAN_TWEETS_CSV, 
        dtype=TWEET_DTYPE, 
        parse_dates=['created_at', 'retweet_created_at']
    )

    logger.info("START - Text transformations")
    if adhoc:
        tweets_df = _get_adhoc_tweets_df(tweets_df)
    text_df = get_text_dt(tweets_df)
    logger.info("END - Text transformations")
    text_df.to_csv(
        TEXT_TWEETS_CSV.replace('tweets.csv', 'tweets-lemmatized-wordgrams.csv'), 
        encoding='utf-8', 
        index=False, 
        quoting=csv.QUOTE_ALL
    )

# %%
if __name__ == '__main__':
    tweets()