"""scrape_users.py

Inputs:
- user_ids (~/scrape_tweets/profiles_get_tweets.csv || ~/input/users.csv)
- user_info (~/input/users-info.csv)
    * user information schema (required columns)

Workflow:
1. Collect new users
    - get existing user_ids (input)
    - for each user_id:
        * collect all_followers (endpoint: get_follower_ids)
        * collect all_friends (endpoint: get_friend_ids)
    - create a new list of user_ids (user_ids + all_followers + all_friends): all_user_ids
    - overwrite existing user_ids
2. Collect user information
    - get existing user_info (input)
    - exclude all_user_ids with existing user_ids from user_info
    - collect all_user_info (endpoint: user_lookup)
    - create a new list of user_info (all_user_info) and apply the user information schema
    - overwrite existing user_info
"""
import scrape_user_ids
import scrape_user_objs


if __name__ == '__main__':
    #scrape_user_ids()
    #scrape_user_objs()
    pass
