import tweepy

def connect_to_twitter():
    # Twitter credentials
    """ICECREAM2 CREDENTIALS """
    consumer_key = 'm3NrMZ7PB4WVrDYAekQEr7mug'
    consumer_secret = 'Pjl6UWbaye7PrP697nv5YHKngwcqnhVMAXdAtRCEJ02ppVXlVj'
    access_key = '1316409694760689666-YSi25euJltCKcDWI1XeM24LUiK4uG5'
    access_secret = 'cb3MG4RJeFkwt2FmHhgIH0V7OfijuN3MxXCcA1P3ntKlP'
    
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth) # wait_on_rate_limit=True
    print('Twitter API working!')
    
    return api
