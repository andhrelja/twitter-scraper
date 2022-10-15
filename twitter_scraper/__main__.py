from . import utils
from . import scrape
from . import clean
from . import graph

logger = utils.get_logger(__file__)
apis = utils.get_api_connections()

logger.info("********************** USERS **********************")
logger.info("---------------- scrape.user_objs ---------------")
scrape.user_objs(apis)
logger.info("------------------ clean.users ------------------")
clean.users()
clean.update_filtered_baseline()
logger.info("----------------- scrape.user_ids ----------------")
scrape.user_ids(apis)
logger.info("******************** END USERS ********************")


logger.info("********************** TWEETS **********************")
logger.info("------------------ scrape.tweets -----------------")
scrape.tweets(apis)
logger.info("------------------ clean.tweets ------------------")
clean.tweets()
logger.info("******************** END TWEETS ********************")


logger.info("********************** GRAPH **********************")
logger.info("------------------ graph.nodes ------------------")
graph.nodes()
logger.info("------------------ graph.edges ------------------")
graph.edges(user_followers=True, user_mentions=True, user_retweets=True)
logger.info("******************** END GRAPH ********************")


logger.info("****************** UPDATE BASELINE ******************")

logger.info("--------------- utils.update_baseline ---------------")
utils.update_baseline(
    archive=True, 
    user_friends=True,
    user_mentions=True,
    user_retweets=True
)

logger.info("**************** END UPDATE BASELINE ****************")

utils.notify()

logger.info("********************** DONE **********************")
