#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 21:28:46 2020

@author: ice-cream
"""
import pandas as pd
import networkx as nx

from tweepy import OAuthHandler
import tweepy
import pandas as pd
import numpy as np
import time
import datetime

def connect_to_twitter():
    # Twitter credentials
    """ICECREAM2 CREDENTIALS """
    consumer_key = 'm3NrMZ7PB4WVrDYAekQEr7mug'
    consumer_secret = 'Pjl6UWbaye7PrP697nv5YHKngwcqnhVMAXdAtRCEJ02ppVXlVj'
    access_key = '1316409694760689666-YSi25euJltCKcDWI1XeM24LUiK4uG5'
    access_secret = 'cb3MG4RJeFkwt2FmHhgIH0V7OfijuN3MxXCcA1P3ntKlP'
    
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)#wait_on_rate_limit=True
    print('Twitter API working!')
    
    return api


def get_followers_ids(user_id):
    root = api.get_user(user_id)
    twitter_screen_name = root.screen_name
    #print('get_followers_ids function working on: ' + twitter_screen_name)
    try:
        followers_ids = []
        for page in tweepy.Cursor(api.followers_ids, screen_name=twitter_screen_name).pages():
            followers_ids.extend(page)
            #time.sleep(10)
        #print(str(twitter_screen_name) + " has " + str(len(followers_ids)) + " followers")
    
    except BaseException as e:
        #print('failed on_status,',str(e))
        time.sleep(3)
        
    return followers_ids


def get_friends_ids(user_id):
    root = api.get_user(user_id)
    twitter_screen_name = root.screen_name
    #print('get_friends_ids function working on: ' + twitter_screen_name)
    try:
        friends_ids = []
        for page in tweepy.Cursor(api.friends_ids, screen_name=twitter_screen_name).pages():
            friends_ids.extend(page)
            #time.sleep(10)
        #print(str(twitter_screen_name) + " is following " + str(len(friends_ids)) + " friends")
    
    except BaseException as e:
        #print('failed on_status,',str(e))
        time.sleep(3)
        
    return friends_ids


df = pd.read_csv('scrape_for_net.csv', index_col=0)

df = df[df.profile_id != -1]
df = df.sort_values(['Followers', 'Friends'], ascending=True)

list_of_all_ids = list(df.profile_id.map(lambda x: '{:.0f}'.format(x)))

api = connect_to_twitter()
G = nx.DiGraph()

counter = 0
start = time.time()

failed_profiles_counter = 0

for profile_id in list_of_all_ids:

    if counter % 1000 == 0:
        time_pass = time.time()-start
        res = time.strftime("%H:%M:%S",time.gmtime(time_pass))
        print(res)
        start = time.time()
    
    try:
        followers_ids = get_followers_ids(profile_id)
        
        for follower_id in followers_ids: 
            if str(follower_id) in list_of_all_ids:
                G.add_edge(str(follower_id), str(profile_id))
        
        friends_ids = get_friends_ids(profile_id) 
        
        for friend_id in friends_ids:
            if str(friend_id) in list_of_all_ids:
                G.add_edge(str(profile_id),  str(friend_id))
        
    
    except tweepy.TweepError:
        failed_profiles_counter +=1
              
    counter += 1
    print(counter)
    nx.write_gml(G, "test_twitter.gml")

#profile_ids = profile_ids.drop_duplicates()
#profile_ids = profile_ids.drop(profile_ids == -1)