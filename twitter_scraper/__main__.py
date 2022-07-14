from . import utils
from . import scrape
from . import clean
from . import graph
from .utils import update_baseline

logger = utils.get_logger(__file__)
apis = utils.get_api_connections()

# logger.info("---------------------- SCRAPE ----------------------")
# scrape.user_ids(apis)
# scrape.user_objs(apis)
# scrape.tweets(apis)
# logger.info("-------------------- END SCRAPE --------------------")


# logger.info("---------------------- CLEAN ----------------------")
# clean.users()
# clean.tweets()
# logger.info("-------------------- END CLEAN --------------------")


logger.info("---------------------- GRAPH ----------------------")
graph.nodes()
graph.edges(user_followers=True, user_mentions=True)
logger.info("-------------------- END GRAPH --------------------")


# logger.info("----------------- UPDATE BASELINE -----------------")
# update_baseline.update_baseline(
#     archive=True, 
#     clean=True, 
#     update=True
# )
# logger.info("--------------- END UPDATE BASELINE ---------------")

logger.info("----------------------- DONE -----------------------")
