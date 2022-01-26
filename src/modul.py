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

