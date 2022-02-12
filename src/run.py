import utils

apis = utils.get_api_connections()
#utils.sample_baseline(10)

import scrape
import clean

scrape.user_ids(apis)
scrape.user_objs(apis)
scrape.tweets(apis)

clean.users()
clean.tweets()
