# Modules

## Scrapers

The :py:mod:twitter_scraper.scrape module consists from three sub-modules.
The following modules collect data using their respected Twitter endpoints:


1. :py:mod:twitter_scraper.scrape.tweets

    
        * [statuses/user_timeline](https://developer.twitter.com/en/docs/twitter-api/v1/tweets/timelines/api-reference/get-statuses-user_timeline)


                * loads history using Tweet IDs: `since_id=None, max_id=None`


                * loads incremental using Tweet IDs: `since_id=max_latest_id, max_id=None`


                * limit: 


                        * 900 requests / 15 mins (using 9 threads = **8100 requests / 15 mins**)


                        * 3200 of a user’s most recent Tweets


                * output: `~/data/output/scrape/tweets/<user-id>.json`


2. :py:mod:twitter_scraper.scrape.user_ids

    
        * [followers/ids](https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-followers-ids)


                * loads all follower ids for every baseline User ID (~/data/input/baseline-user-ids.json\`\`)


                * limit: 15 requests / 15 mins (using 9 threads = **135 requests / 15 mins**)


                * output: `~/data/output/scrape/users/ids/<user-id>.json`


        * [friends/ids](https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-friends-ids)


                * loads all friend ids for every baseline User ID (~/data/input/baseline-user-ids.json\`\`)


                * limit: 15 requests / 15 mins (using 9 threads = **135 requests / 15 mins**)


                * finds missing User IDs (~/data/input/missing-user-ids.json\`\`)


                * output: `~/data/output/scrape/users/ids/<user-id>.csv`


3. :py:mod:twitter_scraper.scrape.user_obj

    
        * [users/show](https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-users-show)


                * loads all user objects for every baseline User ID (~/data/input/baseline-user-ids.json\`\`)


                * limit: 15 requests / 15 mins (using 9 threads = **135 requests / 15 mins**)


                * filter missing User IDs (~/data/input/missing-user-ids.json\`\`)


                * filter processed User IDs (~/data/input/processed-user-ids.json\`\`)


                * output: 


                        * `~/data/input/processed-user-ids.json`


                        * `~/data/output/scrape/users/objs/user-objs.csv`

## User IDs Scraper

### Input

`~/data/input/baseline-user-ids.json`

### Output

`~/data/output/scrape/users/ids/<user-id>.json`

Uses [followers/ids](https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-followers-ids) 
and [friends/ids](https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-friends-ids) 
to collect follower and friend IDs for a given User ID.

This data is later used to generate Graph edges by :mod:twitter_scraper.graph.edges.

By collecting followers and friends data, this module creates a graph node similar to the following:

```json
{
    "<user-id>": {
        "friends_count": 8,
        "followers_count": 6,
        "friends": [
            848904702,
            219350809,
            536230802,
            3028905893,
            214826344,
            2801523007,
            1008662348,
            614676639
        ],
        "followers": [
            91446501,
            214826344,
            269747126,
            219350809,
            536230802,
            848904702
        ]
    }
}
```

## User Scraper

### Input

`~/data/input/baseline-user-ids.json`

### Output

`~/data/output/scrape/users/objs/user-objs.csv`

Uses [users/show](https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-users-show) 
to collect User object for a given user ID.

Applies transformations to API response data. Original tweet JSON:

```json
```

is transformed using the following mapping:

```python
SCRAPE_USER = lambda x: {
    'user_id':          x.get('id'),
    'user_id_str':      x.get('id_str'),
    'name':             x.get('name'),
    'screen_name':      x.get('screen_name'),
    'location':         x.get('location'),
    "profile_location": x.get('profile_location'),
    'derived':          x.get('derived'),
    'url':              x.get('url'),
    'description':      x.get('description'),
    'protected':        x.get('protected'),
    'verified':         x.get('verified'),
    'followers_count':  x.get('followers_count'),
    'friends_count':    x.get('friends_count'),
    'listed_count':     x.get('listed_count'),
    'favourites_count': x.get('favourites_count'),
    'statuses_count':   x.get('statuses_count'),
    'created_at':       x.get('created_at'),
    'profile_banner_url':      x.get('profile_banner_url'),
    'profile_image_url_https': x.get('profile_image_url_https'),
    'default_profile':         x.get('default_profile'),
    'default_profile_image':   x.get('default_profile_image'),
    'withheld_in_countries':   x.get('withheld_in_countries'),
    'withheld_scope':          x.get('withheld_scope'),
}
```

## Tweets Scraper

### Input

`~/data/input/baseline-user-ids.json` #1

### Output

`~/data/output/scrape/users/ids/<user-id>.json`

Uses [user_timeline](https://developer.twitter.com/en/docs/twitter-api/v1/tweets/timelines/api-reference/get-statuses-user_timeline) to collect tweets for a given user ID.

Applies transformations to API response data. Original tweet JSON:

```json
```

is transformed using the following mapping:

```python
SCRAPE_TWEET = lambda x, api=None: {
    'id':                   x.get('id'),
    'user_id':              x.get('user', {}).get('id'),
    'user_id_str':          x.get('user', {}).get('id_str'),
    'full_text':            x.get('full_text', x.get('text')),
    'created_at':           x.get('created_at'),
    'hashtags':             flatten_dictlist(x.get('entities', {}).get('hashtags', []), 'text'),
    'user_mentions':        flatten_dictlist(x.get('entities', {}).get('user_mentions', []), 'id'),
    'retweet_count':        x.get('retweet_count'),
    'retweeter_ids':        [],# api.get_retweeter_ids(x.get('id')),
    'retweet_from_user_id':         x.get('retweeted_status', {}).get('user', {}).get('id'),
    'retweet_from_user_id_str':     str(x.get('retweeted_status', {}).get('user', {}).get('id')),
    'in_reply_to_status_id':        x.get('in_reply_to_status_id'),
    'in_reply_to_status_id_str':    x.get('in_reply_to_status_id_str'),
    'in_reply_to_user_id':          x.get('in_reply_to_user_id'),
    'in_reply_to_user_id_str':      x.get('in_reply_to_user_id_str'),
    'in_reply_to_screen_name':      x.get('in_reply_to_screen_name'),
    'geo':                  x.get('geo'),
    'coordinates':          x.get('coordinates'),
    'place':                x.get('place'),
    'contributors':         x.get('contributors'),
    'is_quote_status':      x.get('is_quote_status'),
    'favorite_count':       x.get('favorite_count'),
    'favorited':            x.get('favorited'),
    'retweeted':            x.get('retweeted'),
    'possibly_sensitive':   x.get('possibly_sensitive'),
    'lang':                 x.get('lang')
}
```


### twitter_scraper.scrape.tweets.get_tweet_max_id(user_id: int)
Reads the user’s scraped tweet JSON and returns the latest tweet ID. 
Latest tweet ID value is used as `since_id` for incremental loads.


* **Parameters**

    **user_id** (*int*) – User ID



* **Returns**

    Latest tweet ID if exists, else None



* **Return type**

    Union[int, NoneType]



### twitter_scraper.scrape.tweets.tweets(apis: List[dict])

1. Creates tweet scrape directory


2. Enqueues user IDs from `baseline-user-ids.json`


3. Starts a :py:func:__collect_user_tweets thread for each connection in :py:mod:twitter_scraper.settings


4. Waits until all threads complete executing


* **Parameters**

    **apis** (*List**[**dict**]*) – list of dictionaries: `[{connection_name: tweepy.API}]`


## Cleaners

The :py:mod:twitter_scraper.clean module consists from three sub-modules.
The following modules clean the collected data output by :py:mod:twitter_scraper.scrape


1. :py:mod:twitter_scraper.clean.tweets

    
        * input: `~/data/output/scrape/tweets/<user-id>.json`


        * output: `~/data/output/clean/tweet/YYYY-MM-DD/tweets.csv`


2. :py:mod:twitter_scraper.clean.users

    
        * input: `~/data/output/scrape/users/objs/user-objs.csv`


        * output: `~/data/output/clean/user/YYY-MM-DD/users.csv`

## Tweets Cleaner

### Input

`~/data/output/scrape/tweets/<user-id>.json`

### Output

`~/data/output/clean/tweet/YYYY-MM-DD/tweets.csv`

Filter Tweets from 2021-08-01 onwards.

Conforms Tweet data to the following :py:mod:pandas schema:

```python
TWEET_DTYPE = {
    'id':               'string',
    'user_id':          'int64',
    'user_id_str':      'string',
    'full_text':        'string',
    'created_at':       'object',
    'hashtags':         'object',
    'user_mentions':    'object',
    'retweet_from_user_id':     'int64',
    'retweet_from_user_id_str': 'string',
    #'in_reply_to_status_id':      pd.Int64Dtype(),
    # 'in_reply_to_status_id_str':  'string',
    #'in_reply_to_user_id':        pd.Int64Dtype(),
    # 'in_reply_to_user_id_str':    'string',
    # 'in_reply_to_screen_name':    'string',
    'geo':              'object',
    'coordinates':      'object',
    # 'place':          'object',
    # 'contributors':   'object',
    # 'is_quote_status': 'bool',
    'retweet_count':    'int',
    'favorite_count':   'int',
    # 'favorited':      'bool',
    # 'retweeted':      'bool',
    # 'possibly_sensitive': 'bool',
    # 'lang': 'string',

    ### Custom columns
    'week': 'string',
    'month': 'string',
    'is_covid': 'bool'
}
```

## Users Cleaner

### Input

`~/data/output/scrape/users/objs/user-objs.csv`

### Output

`~/data/output/clean/user/YYYY-MM-DD/users.csv`

Filter Users based on:
\* protected = False
\* is_croatian = True
\* statuses_count > 10
\* friends_count > 10
\* friends_count < 5000
\* followers_count > 10
\* followers_count < 5000

Conforms User data to the following :py:mod:pandas schema:

```python
USER_DTYPE = {
    'user_id':          'int64',
    'user_id_str':      'string',
    'name':             'string',
    'screen_name':      'string',
    'location':         'string',
    # "profile_location": 'object',
    # 'derived':          'string',
    # 'url':              'string',
    'description':      'string',
    'protected':        'boolean',
    'verified':         'boolean',
    'followers_count':  'int',
    'friends_count':    'int',
    'listed_count':     'int',
    'favourites_count': 'int',
    'statuses_count':   'int',
    'created_at':       'str',
    # 'profile_banner_url':      'string',
    # 'profile_image_url_https': 'string',
    # 'default_profile':         'object',
    # 'default_profile_image':   'string',
    # 'withheld_in_countries':   'object',
    # 'withheld_scope':          'object',

    ### Custom columns
    'is_croatian':      'bool',
    'clean_location':   'string',
}
```
