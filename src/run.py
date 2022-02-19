import utils

apis = utils.get_api_connections()
logger = utils.get_logger(__file__)

import scrape
import clean


logger.info("---------------------- SCRAPE ----------------------")
scrape.user_ids(apis)
scrape.user_objs(apis)
scrape.tweets(apis)

logger.info("---------------------- CLEAN ----------------------")
clean.users()
clean.tweets(nodes=True, edges=True)

# logger.info("----------------- UPDATE BASELINE -----------------")
# scrape.update_baseline()
# clean.update_baseline()

logger.info("----------------------- DONE -----------------------")
