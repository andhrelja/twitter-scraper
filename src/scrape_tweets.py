import tweepy


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
