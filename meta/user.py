# Reference https://developer.twitter.com/en/docs/twitter-api/v1/data-dictionary/object-model/user
import numpy as np


USER_MODEL = {
	'id': np.int64,
    'id_str': str,
    'name': str,
    'screen_name': str,
    'location': str,
    'derived': object,
    'url': str,
    'description': str,
    'protected': bool,
    'verified': bool,
    'followers_count': np.int32,
    'friends_count': np.int32,
    'listed_count': np.int32,
    'favourites_count': np.int32,
    'statuses_count': np.int32,
    'created_at': str,
    'profile_banner_url': str,
    'profile_image_url_https': str,
    'default_profile': bool,
    'default_profile_image': bool,
    'withheld_in_countries': list,
    'withheld_scope': str,
}

    