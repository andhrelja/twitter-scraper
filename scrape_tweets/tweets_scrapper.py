#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  8 12:32:35 2020

@author: ice-cream
"""
from tweepy import OAuthHandler
import tweepy
import pandas as pd
import numpy as np
import math
import time
import datetime
from tweepy import OAuthHandler
import tweepy
import  pandas as pd
import json 
import datetime

def connect_to_twitter1():
    consumer_key = 'r1tcZ5XPtMLzBhwNEZjhHb3vV'
    consumer_secret = '7cGo82YQGOYGi3iJ1LJ9YeMP4GA6paIe2kabLLeicjMrUUhXxs'
    access_key = '166318369-AhoqOVupAsjj0EnrVtHY6Pg3izqremykKLvZpjBV'
    access_secret = 'kRCuZRn0j0Iowqd7VBCTQRgYuM5ZpwAc6ViEzmwJtFPcS'
    
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)
    print('CARLOS Twitter API working!')
    
    return api


def connect_to_twitter2():
    consumer_key = 'm3NrMZ7PB4WVrDYAekQEr7mug'
    consumer_secret = 'Pjl6UWbaye7PrP697nv5YHKngwcqnhVMAXdAtRCEJ02ppVXlVj'
    access_key = '1316409694760689666-YSi25euJltCKcDWI1XeM24LUiK4uG5'
    access_secret = 'cb3MG4RJeFkwt2FmHhgIH0V7OfijuN3MxXCcA1P3ntKlP'
    
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)
    print('IC2 Twitter API working!')
    
    return api


def connect_to_twitter3():
    consumer_key = 'D1cFTRrLpIpJT136NfBo2A0u9' 
    consumer_secret = '3n6YDxzye30OahadlibPcZoh8H6yWB9FQ2x4JfNo4UR0k7m5xH'
    access_key = '1169317946033922048-gnnApT1ZUfmoNeaTOykz9yM2FRsiWL'
    access_secret = 'fN6l6WCjapzwWAW8dU0xiOFExhzeVOHnhmCJg3wwpSopv'
    
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)
    print('IC Twitter API working!')
    
    return api


def get_all_tweets(screen_name, api):
    #Twitter only allows access to a users most recent 3240 tweets with this method
    #initialize a list to hold all the tweepy Tweets
    try:
        alltweets = []  
        
        #make initial request for most recent tweets (200 is the maximum allowed count)
        new_tweets = api.user_timeline(screen_name = screen_name,count=200, tweet_mode="extended")
        
        #save most recent tweets
        alltweets.extend(new_tweets)
        
        #save the id of the oldest tweet less one
        oldest = alltweets[-1].id - 1
        
        #keep grabbing tweets until there are no tweets left to grab
        while len(new_tweets) > 0:
            #print(f"getting tweets before {oldest}")
            
            #all subsiquent requests use the max_id param to prevent duplicates
            new_tweets = api.user_timeline(screen_name = screen_name,count=200,max_id=oldest, tweet_mode="extended")
            
            #save most recent tweets
            alltweets.extend(new_tweets)
            
            #update the id of the oldest tweet less one
            oldest = alltweets[-1].id - 1
            
            #print(f"...{len(alltweets)} tweets downloaded so far")
        
        #transform the tweepy tweets into a 2D array that will populate the csv 
        #outtweets = [[tweet.id_str, tweet.created_at, tweet.text] for tweet in alltweets]
        
        df_tweets_on_profile = pd.DataFrame()
        
        for tweet in alltweets:
            json_str = json.dumps(tweet._json, ensure_ascii=False).encode('utf8')
            jtweet = tweet._json
            
            date = jtweet['created_at'][-4:]   
            if date == '2021' or date == '2022':

                df_json = pd.json_normalize(jtweet)
                df_tweets_on_profile = pd.concat([df_tweets_on_profile, df_json], axis=0) 
    
    except IndexError:
        df_tweets_on_profile = pd.DataFrame()
        
    return df_tweets_on_profile


df = pd.read_csv(r'/home/milky/infocov/scrape_tweets/input/profiles_get_tweets.csv', index_col=0) 

print(df.columns)

#df.columns = ['username', 'statuses'] 
df = df.drop_duplicates(keep='first')

names_to_check = list(df.Username)

api1 = connect_to_twitter1()
api2 = connect_to_twitter2()
api3 = connect_to_twitter3()

df_total = pd.DataFrame()
counter = 0
fail_counter = 0 

names_to_check = names_to_check[counter:]

while len(names_to_check) >= 3:
    if counter % 90 == 0:
        print(counter)
        df_total.to_csv('/home/milky/infocov/scrape_tweets/collected_data/tweets_found_' + str(counter) + '.csv')
        df_total = pd.DataFrame()
        
    df_found = pd.DataFrame()
    
    try:
        df1 = get_all_tweets(names_to_check[0], api1)
        df_found = pd.concat([df_found, df1], axis=0)
        
    except tweepy.TweepError:
        fail_counter +=1
        
    try:
        df2 = get_all_tweets(names_to_check[1], api2)
        df_found = pd.concat([df_found, df2], axis=0)
        
    except tweepy.TweepError:
        fail_counter +=1

    try:
        df3 = get_all_tweets(names_to_check[2], api3)
        df_found = pd.concat([df_found, df3], axis=0)
        
    except tweepy.TweepError:
        fail_counter +=1
        
    df_total = pd.concat([df_total, df_found], axis=0)

    counter +=3
    
    names_to_check = names_to_check[3:]


    