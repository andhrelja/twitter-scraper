"""
graph.nodes
-----------

**Inputs**: 
    1. ``~/data/output/clean/user/YYYY-MM-DD/users.csv``
    2. ``~/data/output/clean/tweet/YYYY-MM-DD/tweets.csv``

**Outputs**: 
    * ``~/data/output/graph/YYYY-MM-DD/nodes.csv``

The custom columns are created using the following rules:

* *total_tweets*: total number of collected Tweets for a given User (Node)
* *covid_tweets*: the number of ``is_covid`` classified Tweets for a given User (Node)
* *covid_pct*: the precentage of ``is_covid`` classified Tweets (total_tweets / covid_tweets) for a given User (Node)
* *is_covid*: a User (Node) is a Covid Tweeter if he has at least one COVID Tweet


Joins User to Tweet data to get only the Users whose Tweets have been collected. Creates the following node attributes:

.. code-block:: python

    NODE_DTYPE = {
        'user_id':          'int64',
        'user_id_str':      'string',
        'followers_count':  'int',
        'friends_count':    'int',
        'listed_count':     'int',
        'favourites_count': 'int',
        'statuses_count':   'int',
        
        ### Custom columns
        'total_tweets':     'int',
        'covid_tweets':     'int',
        'covid_pct':        'float',
        'is_covid':         'bool'
    }



graph.edges
-----------

**Inputs**: 
    1. ``~/data/output/scrape/users/ids/<user-id>.json``
    2. ``~/data/output/clean/tweet/YYY-MM-DD/tweets.csv``
    3. ``~/data/output/graph/YYYY-MM-DD/nodes.csv``

**Outputs**:
    * ``~/data/output/graph/YYY-MM-DD/edges-friends.csv``
    * ``~/data/output/graph/YYY-MM-DD/edges-mentions.csv``
    * ``~/data/output/graph/YYY-MM-DD/edges-retweets.csv``


Creates the following Edge relationships:

1. *User - FRIENDS - User*
    * uses ``~/data/output/scrape/users/ids/<user-id>.json`` to create edges between Users who are friends
2. *User - MENTIONS - User*
    * uses ``~/data/output/clean/tweet/YYY-MM-DD/tweets.csv`` to create edges between Users who mentioned other users in their Tweets
3. *User - RETWEETS - User*
    * uses ``~/data/output/clean/tweet/YYY-MM-DD/tweets.csv`` to create edges between Users who retweeted other users' Tweets

Creates the following edge attributes:

.. code-block:: python

    EDGE_DTYPE = {
        'source': 'int64',
        'target': 'int64',
        'timestamp': 'int64'
    }

"""

from .nodes import nodes
from .edges import edges