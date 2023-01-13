from . import utils
from . import scrape
from . import clean
from . import text
from . import graph

from . import DISCORD_CLIENT
from . import settings

import sys
import argparse

PROG = 'Twitter Scraper'
DESCRIPTION = 'Scrapes and Cleans Croatian Twitter data'
EPILOG = '(C) Faculty of Informatics and Digital Technologies, 2023'
ARGUMENTS = (
    ('-t', '--collect-tweets',
        {'action': 'store_true', 'default': False,
         'help': 'Incrementally collects Tweets and Users for the given baseline-user-ids.json'}),
    ('-f', '--collect-ff',
        {'action': 'store_true', 'default': False,
         'help': 'Collects all Followers and Friends for the given baseline-user-ids.json'}),
)

logger = utils.get_logger(__file__)

parser = argparse.ArgumentParser(
    prog=PROG,
    description=DESCRIPTION,
    epilog=EPILOG
)


def collect_tweets():
    logger.info("********************** USERS **********************")
    apis = utils.get_api_connections()

    logger.info("---------------- scrape.user_objs ---------------")
    scrape.user_objs(apis)
    logger.info("------------------ clean.users ------------------")
    clean.users()
    if not settings.DEBUG:
        clean.update_filtered_baseline()
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
    graph.edges(
        user_followers=False, 
        user_mentions=True, 
        user_retweets=True)
    logger.info("******************** END GRAPH ********************")

    logger.info("********************** TEXT **********************")
    logger.info("------------------ text.tweets ------------------")
    text.tweets()
    logger.info("******************** END TEXT ********************")

    logger.info("****************** UPDATE BASELINE ******************")
    logger.info("--------------- utils.update_baseline ---------------")
    utils.update_baseline(
        archive=True, 
        user_friends=False,
        user_mentions=False,
        user_retweets=True)
    logger.info("**************** END UPDATE BASELINE ****************")


def collect_ff():
    logger.info("****************** FRIENDS & FOLLOWERS ******************")
    apis = utils.get_api_connections()

    logger.info("----------------- scrape.user_ids ----------------")
    scrape.user_ids(apis)
    logger.info("------------------ graph.edges ------------------")
    graph.edges(
        user_followers=True, 
        user_mentions=False, 
        user_retweets=False)
    
    logger.info("--------------- utils.update_baseline ---------------")
    utils.update_baseline(
        archive=True, 
        user_friends=True,
        user_mentions=False,
        user_retweets=False)
    
    logger.info("**************** END FRIENDS & FOLLOWERS ****************")


if __name__ == '__main__':
    for arg, argument, kwargs in ARGUMENTS:
        parser.add_argument(arg, argument, **kwargs)
    
    args = parser.parse_args()
    args_dict = vars(args)
    for f_name, execute in args_dict.items():
        f = getattr(sys.modules[__name__], f_name)
        if execute: f()

    DISCORD_CLIENT.run(settings.DISCORD_TOKEN)
    utils.notify(collect_ff=args_dict['collect_ff'])
