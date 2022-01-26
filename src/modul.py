def get_followers_ids(api, user_id):
    """
    For inputed twitter user id, function returns list of user ids that folow given user.

    Args:
        api (api.API): API object of tweepy.api module
        user_id (str): user twitter id

    Returns:
        list: list of ids
    """

    try:
        followers_ids = []
        for page in tweepy.Cursor(api.followers_ids, user_id=user_id).pages():
            followers_ids.extend(page)
    
    except BaseException as e:
        print('failed on_status,',str(e))
        time.sleep(3)
        
    return followers_ids


def get_friends_ids(api, user_id):
    """
    For inputed twitter user id, function returns list of users ids that given user is following.

    Args:
        api (api.API): API object of tweepy.api module
        user_id (str): user twitter id

    Returns:
        list: list of ids
    """

    try:
        friends_ids = []
        for page in tweepy.Cursor(api.friends_ids, user_id=user_id).pages():
            friends_ids.extend(page)
    
    except BaseException as e:
        print('failed on_status,',str(e))
        time.sleep(3)
        
    return friends_ids


def get_all_tweets(api, user_id):
    """For given user id returns dataframe of up to last 3240 tweets from user profile.
    Each row in the dataframe corresponds to one tweet. 

    Args:
        api (api.API): API object of tweepy.api module
        user_id (str): user twitter id

    Returns:
        DataFrame: pandas dataframe of tweets
    """

    try:
        alltweets = []  
        new_tweets = api.user_timeline(user_id=user_id, count=200, tweet_mode="extended")
        alltweets.extend(new_tweets)
        oldest = alltweets[-1].id - 1
        
        while len(new_tweets) > 0:
            new_tweets = api.user_timeline(user_id=user_id,count=200,max_id=oldest, tweet_mode="extended")
            alltweets.extend(new_tweets)
            oldest = alltweets[-1].id - 1
            
        df_tweets_on_profile = pd.DataFrame()
        
        for tweet in alltweets:
            #json_str = json.dumps(tweet._json, ensure_ascii=False).encode('utf8')
            df_json = pd.json_normalize(tweet._json)
            df_tweets_on_profile = pd.concat([df_tweets_on_profile, df_json], axis=0) 
    
    except IndexError:
        df_tweets_on_profile = pd.DataFrame()
        
    return df_tweets_on_profile


    