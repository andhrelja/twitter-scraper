from pprint import pprint

import stanza
import gensim

from twitter_scraper import settings
from twitter_scraper.utils import fileio

stop_words = fileio.read_content(settings.STOP_WORDS_ENG, 'json')

_tweets = [
    "Donald Trump shows support for Black Lives Matter #BLM during Kansas elections",
    "2022 Kansas elections have the lowest voter turnout since 2018",
    "RT @lightchronicler: When people interact Novak Đoković's #COVID stance takes \"precedence\" over his Grand Slam Tournament victory  😁🌹",
    "2022 Grand Slam Tournament salutes non vaccinated players",
    "This year's open Grand Slam Tournament is hosted by Novak Đoković in Serbia",
    "Riots emerge in the latest Black Lives Matter Kansas rally",
    "Riots keep emerging in ongoing Black Lives Matter rallies",
    "Black Lives Matter keeps getting traction",
    "Mary Smith wins this year's Kansas elections"
]

# Desired outputs
_outputs = [
    [
        "Donald", "Trump", "support", "Black_Lives_Matter", "BLM", "Kansas", "election"
    ],
    [
        "Kansas", "election", "low", "voter", "turnout"
    ]
]


tweets = [gensim.utils.simple_preprocess(tweet) for tweet in _tweets]
tweets = [[word for word in tweet if word not in stop_words] for tweet in tweets]

bigrams = gensim.models.Phrases(sentences=tweets, min_count=1, threshold=8, connector_words=gensim.models.phrases.ENGLISH_CONNECTOR_WORDS)
bigram_model = bigrams.freeze()
# bigram_model.phrasegrams

trigrams = gensim.models.Phrases(sentences=bigram_model[tweets], min_count=2, threshold=8, connector_words=gensim.models.phrases.ENGLISH_CONNECTOR_WORDS)
trigram_model = trigrams.freeze()

bitri_grams = trigrams[bigram_model[tweets]]


nlp = stanza.Pipeline('en', use_gpu=False, processors='tokenize,pos,lemma')

words = set((word for sentence in bitri_grams for word in sentence))
doc = nlp(" ".join(words))
words = {item['text']: item for item in doc.sentences[0].to_dict()}
words.values()

lemmatized_text = [[words[word]['lemma'] for word in sentence] for sentence in bitri_grams]

id2word = gensim.corpora.Dictionary(lemmatized_text)
corpus = [id2word.doc2bow(text) for text in lemmatized_text]

lda_model = gensim.models.LdaModel(
    corpus=corpus,
    id2word=id2word,
    num_topics=3,
    passes=2
)
pprint(lda_model.print_topics())
