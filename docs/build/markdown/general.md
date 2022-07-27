# General

Twitter Scraper is a Python package built using [tweepy](https://www.tweepy.org/), [pandas](https://pandas.pydata.org/) and [networkx](https://networkx.org/).

It accumulates Tweets data using static User objects based in Croatia. User objects can periodically be updated using `twitter_scraper.utils.update_baseline`.

## Legend

![image](/assets/legend.png)


## Activity Diagram

![image](/assets/activity.png)


## Workflow Diagram

![image](/assets/workflow.png)

Twitter Scraper is a Python package performing an ETL workflow over [Twitter API Standard v1.1](https://developer.twitter.com/en/docs/api-reference-index#twitter-api-standard) data.
The workflow runs module-specific jobs sequentially using [threading](https://docs.python.org/3/library/threading.html) [[2](https://realpython.com/intro-to-python-threading/)],
where each connection from `twitter_scraper.settings` runs on a separate thread.
