# General

Twitter Scraper is a Python package built using [tweepy](https://www.tweepy.org/), [pandas](https://pandas.pydata.org/) and [networkx](https://networkx.org/).

It accumulates Tweets data using static User objects based in Croatia. User objects can periodically be updated using `twitter_scraper.utils.update_baseline`.

# Content

1. General
   1. Content
   2. Legend
   3. Activity Diagram
   4. Workflow Diagram

2. Modules
   1. Scrapers
      * scrape.tweets
      * scrape.user_ids
      * scrape.user_objs

   2. Cleaners
      * clean.tweets
      * clean.users

   3. Graph
      * graph.nodes
      * graph.edges

## Legend

![image](/assets/legend.png)


## Activity Diagram

![image](/assets/activity.png)


## Workflow Diagram

![image](/assets/workflow.png)

Twitter Scraper is a Python package performing an ETL workflow over [Twitter API Standard v1.1](https://developer.twitter.com/en/docs/api-reference-index#twitter-api-standard) data.
The workflow runs module-specific jobs sequentially using [threading](https://docs.python.org/3/library/threading.html) [[2](https://realpython.com/intro-to-python-threading/)],
where each connection from `twitter_scraper.settings` runs on a separate thread.

  
# Modules

## Scrapers

The `twitter_scraper.scrape` module transforms the unstructured data, but it doesn’t transform the file’s content.
Scraped data is considered as *golden copy* of the source data. New Tweets data is accumulated using static User (IDs) objects based in Croatia.

This module comprises 3 sub-modules (utilizing 4 Twitter API endpoints):


1. Tweets -  `twitter_scraper.scrape.tweets`

   * [statuses/user_timeline](https://developer.twitter.com/en/docs/twitter-api/v1/tweets/timelines/api-reference/get-statuses-user_timeline)

	 * loads history using Tweet IDs: `since_id=None, max_id=None`
	 * loads incremental using Tweet IDs: `since_id=max_latest_id, max_id=None`
	 * **limits**:
	   * 900 requests / 15 mins (using 9 threads = **8100 requests / 15 mins**)
	   * 3200 of a user’s most recent Tweets
	 * **outputs**:
	   * `~/data/output/scrape/tweets/<user-id>.json`


2. User IDs - `twitter_scraper.scrape.user_ids`

     * [followers/ids](https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-followers-ids)
      	* loads all follower ids for every baseline User ID (`~/data/input/baseline-user-ids.json`)
      	* **limit**: 15 requests / 15 mins (using 9 threads = **135 requests / 15 mins**)
      	* **outputs**:
      		* `~/data/output/scrape/users/ids/<user-id>.json`
     * [friends/ids](https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-friends-ids)
      	* loads all friend ids for every baseline User ID (`~/data/input/baseline-user-ids.json`)
      	* **limit**: 15 requests / 15 mins (using 9 threads = **135 requests / 15 mins**)
      	* finds missing User IDs (`~/data/input/missing-user-ids.json`)
      	* **outputs**:
      		* `~/data/output/scrape/users/ids/<user-id>.csv`


3. User objects - `twitter_scraper.scrape.user_obj`

    * [users/lookup](https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-users-lookup)
     	* loads all user objects for every baseline User ID (`~/data/input/baseline-user-ids.json`)
     	* **limit**: 900 requests / 15 mins (using 9 threads = **8100 requests / 15 mins**)
     	* filter missing User IDs (`~/data/input/missing-user-ids.json`)
     	* filter processed User IDs (`~/data/input/processed-user-ids.json`)
     	* **outputs**:
  			* `~/data/input/processed-user-ids.json`
  			* `~/data/output/scrape/users/objs/user-objs.csv`

### scrape.user_ids


**Endpoints**:
		
* [followers/ids](https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-followers-ids)
* [friends/ids](https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-friends-ids)

**Inputs**: 
		
* `~/data/input/baseline-user-ids.json`

**Outputs**: 

* `~/data/output/scrape/users/ids/<user-id>.json`

By collecting followers and friends data, this module retrieves source data to finally be used as graph **Edges**.

**Example outputs:**

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

This data is later used to generate Graph edges by `twitter_scraper.graph.edges`.

### scrape.user_objs

**Endpoints**: 
	
* [users/lookup](https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-users-lookup)

**Inputs**: 

* `~/data/input/baseline-user-ids.json`
* `~/data/input/processed-user-objs.json`

**Outputs**: 

* `~/data/input/processed-user-objs.json`
* `~/data/output/scrape/users/objs/user-objs.csv`

The output will finally be used as graph **Nodes**.
Applies structural transformations to API response data. Original tweet JSON:

```json
{
	"id": 6253282,
	"id_str": "6253282",
	"name": "Twitter API",
	"screen_name": "TwitterAPI",
	"location": "San Francisco, CA",
	"profile_location": null,
	"description": "The Real Twitter API. Tweets about API changes, service issues and our Developer Platform. Don't get an answer? It's on my website.",
	"url": "https:\/\/t.co\/8IkCzCDr19",
	"entities": {
		"url": {
			"urls": [{
				"url": "https:\/\/t.co\/8IkCzCDr19",
				"expanded_url": "https:\/\/developer.twitter.com",
				"display_url": "developer.twitter.com",
				"indices": [
					0,
					23
				]
			}]
		},
		"description": {
			"urls": []
		}
	},
	"protected": false,
	"followers_count": 6133636,
	"friends_count": 12,
	"listed_count": 12936,
	"created_at": "Wed May 23 06:01:13 +0000 2007",
	"favourites_count": 31,
	"utc_offset": null,
	"time_zone": null,
	"geo_enabled": null,
	"verified": true,
	"statuses_count": 3656,
	"lang": null,
	"contributors_enabled": null,
	"is_translator": null,
	"is_translation_enabled": null,
	"profile_background_color": null,
	"profile_background_image_url": null,
	"profile_background_image_url_https": null,
	"profile_background_tile": null,
	"profile_image_url": null,
	"profile_image_url_https": "https:\/\/pbs.twimg.com\/profile_images\/942858479592554497\/BbazLO9L_normal.jpg",
	"profile_banner_url": null,
	"profile_link_color": null,
	"profile_sidebar_border_color": null,
	"profile_sidebar_fill_color": null,
	"profile_text_color": null,
	"profile_use_background_image": null,
	"has_extended_profile": null,
	"default_profile": false,
	"default_profile_image": false,
	"following": null,
	"follow_request_sent": null,
	"notifications": null,
	"translator_type": null
}
```

is transformed using the following mapping:

```python
SCRAPE_USER = lambda x: {
	'user_id':		  x.get('id'),
	'user_id_str':	  x.get('id_str'),
	'name':			 x.get('name'),
	'screen_name':	  x.get('screen_name'),
	'location':		 x.get('location'),
	"profile_location": x.get('profile_location'),
	'derived':		  x.get('derived'),
	'url':			  x.get('url'),
	'description':	  x.get('description'),
	'protected':		x.get('protected'),
	'verified':		 x.get('verified'),
	'followers_count':  x.get('followers_count'),
	'friends_count':	x.get('friends_count'),
	'listed_count':	 x.get('listed_count'),
	'favourites_count': x.get('favourites_count'),
	'statuses_count':   x.get('statuses_count'),
	'created_at':	   x.get('created_at'),
	'profile_banner_url':	  x.get('profile_banner_url'),
	'profile_image_url_https': x.get('profile_image_url_https'),
	'default_profile':		 x.get('default_profile'),
	'default_profile_image':   x.get('default_profile_image'),
	'withheld_in_countries':   x.get('withheld_in_countries'),
	'withheld_scope':		  x.get('withheld_scope'),
}
```

### scrape.tweets

**Endpoints**: 

* [statuses/user_timeline](https://developer.twitter.com/en/docs/twitter-api/v1/tweets/timelines/api-reference/get-statuses-user_timeline)

**Input**: 

* `~/data/input/baseline-user-ids.json`
* `~/data/output/scrape/users/ids/<user-id>.json` (`max_id`)

**Output**: 

* `~/data/output/scrape/users/ids/<user-id>.json`

Applies structural transformations to API response data. Original tweet JSON:

```json
{
  "created_at": "Thu Apr 06 15:28:43 +0000 2017",
  "id": 850007368138018817,
  "id_str": "850007368138018817",
  "text": "RT @TwitterDev: 1/ Today we’re sharing our vision for the future of the Twitter API platform!nhttps://t.co/XweGngmxlP",
  "truncated": false,
  "entities": {
	"hashtags": [
	  {
		"text": "toninopiculaljudina"
	  },
	  {
		"text": "drugihashtag"
	  }
	],
	"user_mentions": [
	  {
		"id": 2244994945
	  },
	  {
		"id": 837333540
	  }
	],
	"urls": [
	  {
		"extended_url": "https://www.sphinx-doc.org/en/master/usage/restructuredtext/roles.html#role-download"
	  }
	]
  },
  "source": "<a href=\"http://twitter.com\" rel=\"nofollow\">Twitter Web Client</a>",
  "in_reply_to_status_id": null,
  "in_reply_to_status_id_str": null,
  "in_reply_to_user_id": null,
  "in_reply_to_user_id_str": null,
  "in_reply_to_screen_name": null,
  "geo": null,
  "coordinates": null,
  "place": null,
  "contributors": null,
  "retweeted_status": {
	"id": 850006245121695744,
	"entities": {
	  "hashtags": [
		{
		  "text": "toninopiculaljudina"
		},
		{
		  "text": "drugihashtag"
		}
	  ],
	  "user_mentions": []
	},
	"source": "<a href=\"http://twitter.com\" rel=\"nofollow\">Twitter Web Client</a>",
	"in_reply_to_status_id": null,
	"in_reply_to_status_id_str": null,
	"in_reply_to_user_id": null,
	"in_reply_to_user_id_str": null,
	"in_reply_to_screen_name": null,
	"user": {
	  "id": 2244994945
	},
	"geo": null,
	"coordinates": null,
	"place": null,
	"contributors": null,
	"is_quote_status": false,
	"retweet_count": 284,
	"favorite_count": 399,
	"favorited": false,
	"retweeted": false,
	"possibly_sensitive": false,
	"lang": "en"
  },
  "is_quote_status": false,
  "retweet_count": 284,
  "favorite_count": 0,
  "favorited": false,
  "retweeted": false,
  "possibly_sensitive": false,
  "lang": "en"
}
```

is transformed using the following mapping:

```python
SCRAPE_TWEET = lambda x, api=None: {
	'id':				   x.get('id'),
	'user_id':			  x.get('user', {}).get('id'),
	'user_id_str':		  x.get('user', {}).get('id_str'),
	'full_text':			x.get('full_text', x.get('text')),
	'created_at':		   x.get('created_at'),
	'hashtags':			 flatten_dictlist(x.get('entities', {}).get('hashtags', []), 'text'),
	'user_mentions':		flatten_dictlist(x.get('entities', {}).get('user_mentions', []), 'id'),
	'retweet_count':		x.get('retweet_count'),
	'retweeter_ids':		[],# api.get_retweeter_ids(x.get('id')),
	'retweet_from_user_id':		 x.get('retweeted_status', {}).get('user', {}).get('id'),
	'retweet_from_user_id_str':	 str(x.get('retweeted_status', {}).get('user', {}).get('id')),
	'in_reply_to_status_id':		x.get('in_reply_to_status_id'),
	'in_reply_to_status_id_str':	x.get('in_reply_to_status_id_str'),
	'in_reply_to_user_id':		  x.get('in_reply_to_user_id'),
	'in_reply_to_user_id_str':	  x.get('in_reply_to_user_id_str'),
	'in_reply_to_screen_name':	  x.get('in_reply_to_screen_name'),
	'geo':				  x.get('geo'),
	'coordinates':		  x.get('coordinates'),
	'place':				x.get('place'),
	'contributors':		 x.get('contributors'),
	'is_quote_status':	  x.get('is_quote_status'),
	'favorite_count':	   x.get('favorite_count'),
	'favorited':			x.get('favorited'),
	'retweeted':			x.get('retweeted'),
	'possibly_sensitive':   x.get('possibly_sensitive'),
	'lang':				 x.get('lang')
}

flatten_dictlist = lambda dictlist, colname: [_dict.get(colname) for _dict in dictlist]
```

**Example outputs:**

```json
[
  {
	"id": 1548630458245824513,
	"user_id": 146153494,
	"user_id_str": "146153494",
	"full_text": "Mentioning some stuff with @KinderGartenRi \n#COVID19 #funtimes #twitter_scraper",
	"created_at": "Sun Jul 17 11:27:28 +0000 2022",
	"hashtags": [
	  "COVID19",
	  "funtimes",
	  "twitter_scraper"
	],
	"user_mentions": [
	  1488523272891375621
	],
	"retweet_count": 1,
	"retweeter_ids": [],
	"retweet_from_user_id": null,
	"retweet_from_user_id_str": "None",
	"in_reply_to_status_id": null,
	"in_reply_to_status_id_str": null,
	"in_reply_to_user_id": null,
	"in_reply_to_user_id_str": null,
	"in_reply_to_screen_name": null,
	"geo": null,
	"coordinates": null,
	"place": null,
	"contributors": null,
	"is_quote_status": false,
	"favorite_count": 0,
	"favorited": false,
	"retweeted": false,
	"possibly_sensitive": null,
	"lang": "en"
  }
]
```

```json
[
  {
	"id": 1548632334760640513,
	"user_id": 1488523272891375621,
	"user_id_str": "1488523272891375621",
	"full_text": "RT @andhrelja: Mentioning some stuff with @KinderGartenRi \n#COVID19 #funtimes #twitter_scraper",
	"created_at": "Sun Jul 17 11:34:55 +0000 2022",
	"hashtags": [
	  "COVID19",
	  "funtimes",
	  "twitter_scraper"
	],
	"user_mentions": [
	  146153494,
	  1488523272891375621
	],
	"retweet_count": 1,
	"retweeter_ids": [],
	"retweet_from_user_id": 146153494,
	"retweet_from_user_id_str": "146153494",
	"in_reply_to_status_id": null,
	"in_reply_to_status_id_str": null,
	"in_reply_to_user_id": null,
	"in_reply_to_user_id_str": null,
	"in_reply_to_screen_name": null,
	"geo": null,
	"coordinates": null,
	"place": null,
	"contributors": null,
	"is_quote_status": false,
	"favorite_count": 0,
	"favorited": false,
	"retweeted": false,
	"possibly_sensitive": null,
	"lang": "en"
  }
]
```

## Cleaners

Cleaners are fueled by [pandas](https://pandas.pydata.org/) focused on working with `csv` formats. They will
Cleaners transform `twitter_scraper.scrape` outputs by creating artificial content and deleting irrelevant content. They do not interract with data/input/ files.

The `twitter_scraper.clean` module consists from two sub-modules:


1. Tweets - `twitter_scraper.clean.tweets`

	* **inputs**:
		* `~/data/output/scrape/tweets/<user-id>.json`
		* filter 2021-08-01 onwards
	* **outputs**:
		* `~/data/output/clean/tweet/YYYY-MM-DD/tweets.csv`


2. Users - `twitter_scraper.clean.users`

   * **inputs**:
       * `~/data/output/scrape/users/objs/user-objs.csv`
       * `~/data/input/locations.json`
       * filter Croatian Users only
   * **outputs**:
       * `~/data/output/clean/user/YYY-MM-DD/users.csv`

### clean.users

**Inputs**: 

* `~/data/output/scrape/users/objs/user-objs.csv`
* `~/data/input/locations.json`

**Outputs**: 

* `~/data/output/clean/user/YYYY-MM-DD/users.csv`

Artificial columns are created using the following rules:


* *is_croatian*: a User’s location determined using naive text parsing and a static helper file (`locations.json`)
* *clean_location*: whitespace cleaned, user provided location or the value “Hrvatska”


Filter Users based on:

* *protected* = False
* *is_croatian* = True
* *statuses_count* > 10
* *friends_count* > 10
* *friends_count* < 5000
* *followers_count* > 10
* *followers_count* < 5000

Conforms User data to the following `pandas` schema:

```python
USER_DTYPE = {
	'user_id':		  'int64',
	'user_id_str':	  'string',
	'name':			 'string',
	'screen_name':	  'string',
	'location':		 'string',
	'description':	  'string',
	'protected':		'boolean',
	'verified':		 'boolean',
	'followers_count':  'int',
	'friends_count':	'int',
	'listed_count':	 'int',
	'favourites_count': 'int',
	'statuses_count':   'int',
	'created_at':	   'str',

	### Custom columns
	'is_croatian':	  'bool',
	'clean_location':   'string',
}
```

### clean.tweets

**Inputs**: 

* `~/data/output/scrape/tweets/<user-id>.json`

**Outputs**: 
* `~/data/output/clean/tweet/YYYY-MM-DD/tweets.csv`

Filter Tweets from 2021-08-01 onwards. Because this module is focused on working with `csv` formats, it transforms scraped `json` to clean `csv`.
Conforms Tweet data to the following [pandas dtypes](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.dtypes.html):

```python
TWEET_DTYPE = {
	'id':			   'string',
	'user_id':		  'int64',
	'user_id_str':	  'string',
	'full_text':		'string',
	'created_at':	   'object',
	'hashtags':		 'object',
	'user_mentions':	'object',
	'retweet_from_user_id':	 'int64',
	'retweet_from_user_id_str': 'string',
	'geo':			  'object',
	'coordinates':	  'object',
	'retweet_count':	'int',
	'favorite_count':   'int',

	### Custom columns
	'week': 'string',
	'month': 'string',
	'is_covid': 'bool'
}
```

## Graph

Graphs are also fueled by [pandas](https://pandas.pydata.org/), focused on working with csv formats.
Graphs transform `twitter_scraper.clean` outputs by aggregating Tweets (*edges-mentions, edges-retweets*).
They also read information from `twitter_scraper.scrape.user_ids` outputs (*edges-friends*).

The `twitter_scraper.graph` module consists from two sub-modules:


1. Nodes - `twitter_scraper.graph.nodes`
	* inputs:
		1. `~/data/output/clean/user/YYYY-MM-DD/users.csv`
		2. `~/data/output/clean/tweet/YYYY-MM-DD/tweets.csv`
	* output: `~/data/output/graph/YYYY-MM-DD/nodes.csv`

2. Edges - `twitter_scraper.graph.edges`
	* inputs:
      	1. `~/data/output/scrape/users/ids/<user-id>.json`
      	2. `~/data/output/clean/tweet/YYY-MM-DD/tweets.csv`
      	3. `~/data/output/graph/YYYY-MM-DD/nodes.csv`


	* outputs:
      	* `~/data/output/graph/YYY-MM-DD/edges-friends.csv`
      	* `~/data/output/graph/YYY-MM-DD/edges-mentions.csv`
      	* `~/data/output/graph/YYY-MM-DD/edges-retweets.csv`

### graph.nodes

**Inputs**: 

1. `~/data/output/clean/user/YYYY-MM-DD/users.csv`
2. `~/data/output/clean/tweet/YYYY-MM-DD/tweets.csv`

**Outputs**: 

* `~/data/output/graph/YYYY-MM-DD/nodes.csv`

The custom columns are created using the following rules:

* *total_tweets*: total number of collected Tweets for a given User (Node)
* *covid_tweets*: the number of `is_covid` classified Tweets for a given User (Node)
* *covid_pct*: the precentage of `is_covid` classified Tweets (total_tweets / covid_tweets) for a given User (Node)
* *is_covid*: a User (Node) is a Covid Tweeter if he has at least one COVID Tweet

Joins User to Tweet data to get only the Users whose Tweets have been collected. Creates the following node attributes:

```python
NODE_DTYPE = {
	'user_id':		  'int64',
	'user_id_str':	  'string',
	'followers_count':  'int',
	'friends_count':	'int',
	'listed_count':	 'int',
	'favourites_count': 'int',
	'statuses_count':   'int',

	### Custom columns
	'total_tweets':	 'int',
	'covid_tweets':	 'int',
	'covid_pct':		'float',
	'is_covid':		 'bool'
}
```

### graph.edges

**Inputs**: 

1. `~/data/output/scrape/users/ids/<user-id>.json`
2. `~/data/output/clean/tweet/YYY-MM-DD/tweets.csv`
3. `~/data/output/graph/YYYY-MM-DD/nodes.csv`

**Outputs**:

* `~/data/output/graph/YYY-MM-DD/edges-friends.csv`
* `~/data/output/graph/YYY-MM-DD/edges-mentions.csv`
* `~/data/output/graph/YYY-MM-DD/edges-retweets.csv`

Creates the following Edge relationships:


1. *User - FRIENDS - User*

		
   * uses `~/data/output/scrape/users/ids/<user-id>.json` to create edges between Users who are friends


1. *User - MENTIONS - User*


   * uses `~/data/output/clean/tweet/YYY-MM-DD/tweets.csv` to create edges between Users who mentioned other users in their Tweets


3. *User - RETWEETS - User*


   * uses `~/data/output/clean/tweet/YYY-MM-DD/tweets.csv` to create edges between Users who retweeted other users’ Tweets

Creates the following edge attributes:

```python
EDGE_DTYPE = {
	'source': 'int64',
	'target': 'int64',
	'timestamp': 'int64'
}
```
