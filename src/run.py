import utils

apis = utils.get_api_connections()
logger = utils.get_logger(__file__)

import scrape
import clean
import graph
from twitter_scraper import update_baseline


logger.info("---------------------- SCRAPE ----------------------")
scrape.user_ids(apis)
scrape.user_objs(apis)
scrape.tweets(apis)

logger.info("---------------------- CLEAN ----------------------")
clean.users()
clean.tweets()

logger.info("---------------------- GRAPH ----------------------")
graph.nodes()
graph.edges(user_followers=True, user_mentions=False)

logger.info("----------------- UPDATE BASELINE -----------------")
update_baseline.update_baseline(
    archive=True, 
    clean=True, 
    update=True
)

logger.info("----------------------- DONE -----------------------")
