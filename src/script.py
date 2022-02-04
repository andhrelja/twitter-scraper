import re
import os
import sys
import time 
import string

import numpy as np
import pandas as pd 
import networkx as nx
from statistics import mean
import matplotlib.pyplot as plt

from nltk.tokenize import word_tokenize
from collections import Counter
import spacy_udpipe


def users_mention(G, created_at, tweet_id, user_id, mentioned_user_ids_list):
    tweet_id = str(int(tweet_id))

    if len(mentioned_user_ids_list) > 0: 

        for mentioned_user_id in mentioned_user_ids_list:

            if G.has_edge(user_id, mentioned_user_id):
                G[user_id][mentioned_user_id]['weight'] +=1
                G[user_id][mentioned_user_id]['tweetInfo'].update({tweet_id: created_at})

            else: 
                G.add_edge(user_id, mentioned_user_id, created_at=str(created_at),
                tweetInfo={tweet_id: created_at}, weight=1)


def create_users_mention_layer(df, SAVE_LOCATION, GRAPH_FORMAT):
    """ 
    ##? USERS MENTION 
    """
    df_selection = df[['created_at', 'id_str', 'user.id', 'mentioned_users_ids']]
    # df_selection['mentioned_users_ids'] = df_selection['entities.user_mentions'].map(lambda x: get_mentioned_user_info(x))
    # df_selection['mentioned_users_usernames'] = df_selection['entities.user_mentions'].map(lambda x: get_mentioned_user_name(x))
    
    # df_selection = df_selection.drop(columns=['entities.user_mentions'])
    df_selection = df_selection[df_selection['mentioned_users_ids'].map(len) > 0]

    G = nx.DiGraph()
    G.add_nodes_from(list(df_selection['user.id'].unique()))
    mentioned_users_ids_list = list(set(sum(list(df_selection.mentioned_users_ids), [])))
    G.add_nodes_from(mentioned_users_ids_list)

    df_selection.apply(lambda x : users_mention(G, x['created_at'], x['id_str'], x['user.id'], x['mentioned_users_ids']), axis = 1) 
    
    nx.write_gexf(G, SAVE_LOCATION + "/users_mention" + GRAPH_FORMAT)
    print('USERS MENTION for there is number_of_nodes: {} and number_of_edges: {} and type of graph is {}'.format(G.number_of_nodes(), G.number_of_edges(), type(G) ))


def user_reply(G, created_at, tweetId, user_id, in_reply_user_id_str):
    tweetId = str(int(tweetId))

    if G.has_edge(user_id, in_reply_user_id_str):
        G[user_id][in_reply_user_id_str]['weight'] +=1
        G[user_id][in_reply_user_id_str]['tweetInfo'].update({tweetId: created_at})

    else: 
        G.add_edge(user_id, in_reply_user_id_str, created_at=str(created_at),
        tweetInfo={tweetId: created_at}, weight=1)


def create_users_reply_layer(df, SAVE_LOCATION, GRAPH_FORMAT):
    """
    ##? USERS REPLY GRAPH
    """
    graph_name = "users_reply_layer"
    G = nx.DiGraph()
    df_selection = df[df['in_reply_to_user_id_str'].notna()]

    G.add_nodes_from(list(df_selection['user.id'].unique()))
    G.add_nodes_from(list(df_selection.in_reply_to_user_id_str.unique()))

    df_selection.apply(lambda x : user_reply(G, x['created_at'], x['id_str'], x['user.id'], x['in_reply_to_user_id_str']), axis = 1) 
    
    nx.write_gexf(G, SAVE_LOCATION + "/users_reply" + GRAPH_FORMAT)

    print('USERS REPLY GRAPH there is number_of_nodes: {} and number_of_edges: {} and type of graph is {}'.format(G.number_of_nodes(), G.number_of_edges(), type(G) ))


def user_quote(G, created_at, tweet_id, user_id, in_reply_user_id_str):
    tweet_id = str(int(tweet_id))

    if G.has_edge(user_id, in_reply_user_id_str):
        G[user_id][in_reply_user_id_str]['weight'] +=1
        G[user_id][in_reply_user_id_str]['tweetInfo'].update({tweet_id: created_at})

    else: 
        G.add_edge(user_id, in_reply_user_id_str, tweetInfo={tweet_id: created_at}, weight=1)


def user_retweet(G, created_at, tweet_id, user_id, retweeting_user_id_str):
    tweet_id = str(int(tweet_id))

    if G.has_edge(user_id, retweeting_user_id_str):
        G[user_id][retweeting_user_id_str]['weight'] +=1
        G[user_id][retweeting_user_id_str]['tweetInfo'].update({tweet_id: created_at})

    else: 
        G.add_edge(user_id, retweeting_user_id_str, created_at=str(created_at),
        tweetInfo={tweet_id: created_at}, weight=1)


def count_of_intersection_terms(list_1, list_2):
    
    return len(set(list_1).intersection(set(list_2)))


def create_edges(G, created_at, tweet_id, created_at_, tweet_id_, count_of_intersection_terms):
    if tweet_id != tweet_id_:
        if created_at > created_at_:
            if G.has_edge(tweet_id, tweet_id_):
                pass

            else: 
                G.add_edge(tweet_id, tweet_id_, weight=count_of_intersection_terms)

        else:

            if G.has_edge(tweet_id_, tweet_id):
                pass

            else: 
                G.add_edge(tweet_id_, tweet_id, weight=count_of_intersection_terms)


def create_tweets_keywords_layer(df, COMMON_TERMS_TRESHOLD, SAVE_LOCATION, GRAPH_FORMAT):
    df_ = df.copy()
    df_ = df_[['created_at', 'id_str', 'user.id', 'full_text_clean']]
    df_ = df_[df_['full_text_clean'].map(len) >= COMMON_TERMS_TRESHOLD]

    G = nx.DiGraph()
    G.add_nodes_from(list(df.id_str.unique()))

    while len(df_) > 1:

        first_row_of_df = df_.head(1)
        first_element_terms = first_row_of_df.iloc[0]['full_text_clean']
        created_at = first_row_of_df.iloc[0]['created_at']
        tweet_id = first_row_of_df.iloc[0]['id_str']
        df_ = df_[1:] 

        df_['count_of_intersection_terms'] = df.full_text_clean.apply(lambda x: count_of_intersection_terms(x, first_element_terms))

        df_selection = df_[df_['count_of_intersection_terms'] >= COMMON_TERMS_TRESHOLD]
        df_selection.apply(lambda x: tf.create_edges(G, created_at, tweet_id, x['created_at'], x['id_str'], x['count_of_intersection_terms']), axis = 1)

    nx.write_gexf(G, SAVE_LOCATION + "tweets_keywords_" + str(COMMON_TERMS_TRESHOLD) + GRAPH_FORMAT)

    print('RETWEET NEW for number_of_common_terms = {}, there is number_of_nodes: {} and number_of_edges: {}'.format(COMMON_TERMS_TRESHOLD, G.number_of_nodes(), G.number_of_edges()))

    return G


# def create_tweets_keywords_layerOLD(df, COMMON_TERMS_TRESHOLD, SAVE_LOCATION, GRAPH_FORMAT): 
#     """ use case of how not to make functions and code, but it works!"""
    
#     def wire_tweets(df_, created_at, tweet_id, keywords_and_hashtags):
#         """
#         """
#         global COMMON_TERMS_TRESHOLD

#         def create_edges(created_at, tweet_id, keywords_and_hashtags, created_at_, tweet_id_, keywords_and_hashtags_):
        
#             shared_keywords_hashtags = len(set(keywords_and_hashtags).intersection(set(keywords_and_hashtags_)))
            
#             global G

#             if shared_keywords_hashtags >= COMMON_TERMS_TRESHOLD:
#                 if tweet_id != tweet_id_:
#                     if created_at > created_at_:

#                         if G.has_edge(tweet_id, tweet_id_):
#                             pass

#                         else: 
#                             G.add_edge(tweet_id, tweet_id_, weight=shared_keywords_hashtags)

#                     else:

#                         if G.has_edge(tweet_id_, tweet_id):
#                             pass

#                         else: 
#                             G.add_edge(tweet_id_, tweet_id, weight=shared_keywords_hashtags)


#         selection = df_[df_.full_text_clean.apply(lambda x: any(item for item in keywords_and_hashtags if item in x))]

#         selection.apply(lambda x: create_edges(created_at, tweet_id, keywords_and_hashtags,
#                                                 x['created_at'], x['id_str'], x['full_text_clean']), axis = 1)

#         df_ = df_[1:]


#     df_ = df.copy()
#     df_ = df[df['full_text_clean'].map(len) > COMMON_TERMS_TRESHOLD]
#     df_ = df_[['created_at', 'id_str', 'user.id', 'full_text_clean']]

#     G = nx.DiGraph()
#     G.add_nodes_from(list(df.id_str.unique()))

#     df_['created_at'] = pd.to_datetime(df_['created_at'], utc=True)

#     start_time = time.time()

#     df_selection = df_.copy()
#     df_selection.apply(lambda x: wire_tweets(df_, x['created_at'], x['id_str'], x['full_text_clean']), axis = 1)

#     print("runtime: {:.2f} seconds".format(time.time() - start_time))
#     print('RETWEET OLD for number_of_common_terms = {}, there is number_of_nodes: {} and number_of_edges: {}'.format(COMMON_TERMS_TRESHOLD,
#     G.number_of_nodes(), G.number_of_edges()))




def get_mentioned_user_info(input_string):
    users_mentioned = []
    try:
        l = eval(input_string)
    except:
        return np.nan

    try:
        for elem in l:
            try:
                d = eval(str(elem))
                users_mentioned.append(d['id_str'])

            except [KeyError, NameError]:
                return []

    except TypeError:
        return []

    if len(users_mentioned) == 0:
        return []

    else:
        return users_mentioned


def get_mentioned_user_name(input_string):
    users_mentioned = []
    try:
        l = eval(input_string)
    except:
        return [] #np.nan

    try:
        for elem in l:
            try:
                d = eval(str(elem))
                users_mentioned.append(d['screen_name'])

            except [KeyError, NameError]:
                return [] #np.nan

    except TypeError:
        return [] #np.nan

    if len(users_mentioned) == 0:
        return [] #np.nan

    else:
        return users_mentioned


def get_hashtags(input_string):
    users_mentioned = []

    empty_list = []
    try:
        l = eval(input_string)
    except:
        return empty_list

    try:
        for elem in l:
            try:
                d = eval(str(elem))
                users_mentioned.append(d['text'])

            except [KeyError, NameError]:
                return empty_list

    except TypeError:
        return empty_list

    if len(users_mentioned) == 0:
        return empty_list

    else:
        return users_mentioned


def get_keywords(input_string):
    keywords = ['koron', 'virus', 'covid', 'kovid', 'karant', 'izolac', 'ostanidoma', 
            'ostanimodoma', 'slusajstruku', 'slušajstruku', 'ostanimoodgovorni',
            'coron', 'sarscov2', 'sars' 'cov2', 'ncov', 'vizir', 'lockd', 'simpto',
            'pfizer', 'moderna', 'astrazeneca', 'sputnik', 'cjep', 'cijep',
            'samoizola', 'viro', 'zaraž', 'zaraz', 'respir', 'testira', 'obolje',
            'nuspoj', 'capak', 'beroš', 'beros' 'markoti', 'alemka',
            'pandem', 'epide', "ljekov", 'propusnic', 'stožer', 'stozer',
            "medicin", 'hzjz', 'antigensk', 'festivala slobode',
            'dezinf', 'infekc', 'inkubacij', 'mask', 'bolnic', 'n95',
            'doktor', 'terapij', 'patoge', 'dijagnost', 'distanc']

    keywords_in_string = []

    for keyword in keywords:

        try:
            if keyword in input_string:
                keywords_in_string.append(keyword)

        except TypeError:
            pass

    if len(keywords_in_string)>= 1:
        return keywords_in_string

    else:
        return []


def calculate_strength(g, weight_value):
    graph_freq = {}
    nodes = list(g.nodes)
    for node in nodes:
        edges = list(g.edges(node, data=True))
    
        freq = 0
        for edge in edges:
            (edge_a, edge_b, data) = edge
            freq += data[weight_value]
        
        graph_freq.update({str(node):freq})
    
    ave_strength_value = mean(graph_freq[k] for k in graph_freq)
    
    return ave_strength_value


def calculate_in_strength(g):
    
    graph_strengths = {}

    for node in list(g.nodes):
        node_ins = list(g.in_edges(node, data=True))
        node_weights = [edge[2]['weight'] for edge in node_ins]

        try:
            node_strength = sum(node_weights)/len(node_weights)
            graph_strengths.update({str(node):node_strength})
        
        except ZeroDivisionError:
            node_strength = 0
            graph_strengths.update({str(node):node_strength})

    ave_strength_value = sum(graph_strengths.values())/len(graph_strengths.values())
    
    return graph_strengths


def calculate_out_strength(g):
    
    graph_strengths = {}

    for node in list(g.nodes):
        node_outs = list(g.out_edges(node, data=True))
        node_weights = [edge[2]['weight'] for edge in node_outs]

        try:
            node_strength = sum(node_weights)/len(node_weights)
            graph_strengths.update({str(node):node_strength})
        
        except ZeroDivisionError:
            node_strength = 0
            graph_strengths.update({str(node):node_strength})

    ave_strength_value = sum(graph_strengths.values())/len(graph_strengths.values())
    
    return graph_strengths


def join_hashtags_and_keywords(hashtags, keywords):
    return list(set(hashtags + keywords))


def check_if_user_id_is_in_net(user_id, all_users_in_net):    
    return user_id in all_users_in_net


def has_covid_keyword(row):
    return len(row) > 0


def create_columns_and_report(df, INPUT_GRAPH_PATH, print_report=True):
    
    G = nx.read_gml(INPUT_GRAPH_PATH)

    # df = df.drop(columns=['Unnamed: 0', 'Unnamed: 0.1', 'Unnamed: 0.1.1'], axis=1)
    df = df[df['retweeted_status.full_text'].isnull()]
    df = df[df['full_text'].notna()]
    df['user.id_str'] = df['user.id_str'].map(lambda x: '{:.0f}'.format(x))

    all_users_in_net = list(set(list(G.nodes())))
    df['user_in_net'] = df['user.id_str'].apply(lambda x: check_if_user_id_is_in_net(x, all_users_in_net))

    df_retweeted = df[df.retweet_count > 0]
    df_not_retweeted = df[df.retweet_count == 0]

    #value_counts = pd.value_counts(df_retweeted['retweet_count']).head(20) #.plot.bar()
    # CHECK IF USER ID IS IN FOLLOW NETWORK 
    #all_users_in_dataset = set(df_retweeted['user.id_str'].map(lambda x: '{:.0f}'.format(x)).tolist())

    df_t = df.drop_duplicates(subset=['user.id_str'], keep='first')
    df_t = df_retweeted.drop_duplicates(subset=['user.id_str'], keep='first')

    df['covid_keywords'] = df['full_text'].apply(lambda x: get_keywords(x)) ## oznaka za covid/non covid
    df['has_covid_keyword'] = df['covid_keywords'].apply(lambda x: has_covid_keyword(x))
    
    if print_report:
        print('Broj tvitova u Org (ukupno) datasetu je: {}'.format(len(df)))
        print('Broj tvitova u Org datasetu koji imaju 1 ili vise retvitova: {}'.format(len(df_retweeted)))
        print('Broj tvitova u Org datasetu koji imaju 0 retvitova: {}'.format(len(df_not_retweeted)))
        print('\nU nastavku: zbroj True i False vrijendost daje ukupan broj jedinstvenih korisnika: ')
        print('Broj korisnika iz Org (ukupno) dataseta ciji ID je u mrezi followera: \n{}'.format(df_t.user_in_net.value_counts()))
        print('Broj korisnika iz Org koji imaju barem jedan retweet ciji ID je u mrezi followera: \n{}'.format(df_t.user_in_net.value_counts()))
        print('\nBroj tvitova je {} a od toga covid ih je: \n{}'.format(len(df), df.has_covid_keyword.value_counts()))
    
    return df


def clean_text(text, cro_sw_lemamatized, lemmatise):
    """ 
    remove punctuation
    leammatize
    remove cro stowords
    """

    text = re.sub(r'http\S+', '', text)

    text = text.replace("č", "c")
    text = text.replace("ć", "c")
    text = text.replace("ž", "z")
    text = text.replace("š", "s")
    text = text.replace("đ", "dj")

    text_tokens = word_tokenize(text)
    text_tokens = [re.sub(r'[^a-zA-Z0-9]', '', text) for text in text_tokens]

    words_lemmatized = []
    for i in text_tokens:
        doc = lemmatise(i)
        try:
            words_lemmatized.append(doc[0].lemma_)
        except:
            pass

    text_tokens = words_lemmatized
    text_tokens = [word for word in text_tokens if not word in cro_sw_lemamatized]

    text_tokens = [x for x in text_tokens if len(x) > 2]

    return text_tokens


def check_len(value_to_check):
    """returns True if len(value_to_check) is larger than 2
    """
    return len(str(value_to_check)) > 3


def create_nodes_vectors(path, graph_name, weight):
    import community as community_louvain
    from scipy.sparse.linalg.eigen.arpack import eigs, ArpackNoConvergence

    g = nx.read_gexf(path)

    print('number_of_nodes: {}'.format(g.number_of_nodes()))
    print('number_of_edges: {}'.format(g.number_of_edges()))

    MAX_ITER = 5000

    measures = {
    'in_degree': lambda g: nx.in_degree_centrality(g),
    'out_degree': lambda g: nx.out_degree_centrality(g),
    'in_strength': lambda g: tf.calculate_in_strength(g),
    'out_strength': lambda g: tf.calculate_out_strength(g),
    'eigenvector_in': lambda g: nx.eigenvector_centrality_numpy(g, weight=weight, max_iter=MAX_ITER),
    'eigenvector_out': lambda g: nx.eigenvector_centrality_numpy(g.reverse(), weight=weight, max_iter=MAX_ITER),
    'katz_in': lambda g: nx.katz_centrality_numpy(g, weight=weight),
    'katz_out': lambda g: nx.katz_centrality_numpy(g.reverse(), weight=weight),
    'clustering': lambda g: nx.clustering(g),
    'louvian_class': lambda g: community_louvain.best_partition(g.to_undirected())
    }

    df_res = pd.DataFrame()

    for _, graph_function in measures.items():
        try:
            node_values = pd.DataFrame.from_dict(graph_function(g), orient='index')

        except Exception as e:
            print('greska: {} sa: {}'.format(e, graph_function))
        

        df_res = pd.concat([df_res, node_values], axis=1)

    df_res.columns = [graph_name.replace('.gml', '') + '_' + x for x in list(measures.keys())]

    return df_res
    
