# Reference https://developer.twitter.com/en/docs/twitter-api/v1/tweets/timelines/api-reference/get-statuses-user_timeline
import numpy as np

TWEET_MODEL = {
	'created_at': str,
	'id': int,
	'id_str': str,
	'text': str,
	'truncated': bool,
	'entities': {
		'hashtags': [],
		'user_mentions': [
			{
				'id': int
			}
		],
	},
	'in_reply_to_status_id': bool,
	'in_reply_to_status_id_str': bool,
	'in_reply_to_user_id': bool,
	'in_reply_to_user_id_str': bool,
	'in_reply_to_screen_name': bool,
	'geo': object,
	'coordinates': object,
	'place': str,
	'contributors': object,
	'retweeted_status': {
 		'user': {
			'id': int
	 	}
	},
	'is_quote_status': bool,
	'retweet_count': np.int32,
	'favorite_count': np.int32,
	'favorited': bool,
	'retweeted': bool,
	'possibly_sensitive': bool,
	'lang': 'en' 
}