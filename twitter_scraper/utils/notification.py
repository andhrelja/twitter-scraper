import os
import discord

from twitter_scraper.utils import fileio
from twitter_scraper import DISCORD_CLIENT
from twitter_scraper import utils
from twitter_scraper import settings


CHANNEL_ID = 1029494278751273011
LOG_OUTPUT_PATH = os.path.join(settings.LOGS_DIR, '{}.json'.format(settings.folder_name))

message = """twitter-scraper outputs:

- Debug = `{debug}`
- Initial baseline size: `{initial_baseline_len}`
- Final baseline size: `{final_baseline_len}`
- Number of Croatian users: `{cro_users_len}`
- User Mentions Graph:
    - found `{found_mentions}/{nodes_len}` nodes
    - found edges for `{len_mentions_source}/{found_mentions}` users
    - found `{len_mentions}` edges
- User Retweets Graph:
    - found `{found_retweets}/{nodes_len}` nodes
    - found edges for `{len_retweets_source}/{found_retweets}` users
    - found `{len_retweets}` edges
"""

message_defaults = {
    'debug': False,
    'initial_baseline_len': 0,
    'final_baseline_len': 0,
    'cro_users_len': 0,
    'nodes_len': 0,
    'found_mentions': 0,
    'found_followers': 0,
    'len_mentions': 0,
    'len_retweets': 0,
    'len_followers': 0,
    'len_followers_source': 0,
    'len_mentions_source': 0,
    'len_retweets_source': 0, 
    'found_retweets': 0,
    'nodes_len': 0,
}


def update_log_outputs():
    global message_defaults
    log_outputs = fileio.read_content(LOG_OUTPUT_PATH, file_type='json')
    initial_baseline_user_ids = fileio.read_content(
        path=os.path.join(settings.INPUT_DIR, 'history', 'clean.users_{}_baseline-user-ids.json'.format(settings.folder_name)),
        file_type='json'
    )
    log_outputs.update({
        'debug': settings.DEBUG,
        'initial_baseline_len': len(initial_baseline_user_ids),
        'final_baseline_len': len(utils.get_baseline_user_ids())
    })
    fileio.write_content(LOG_OUTPUT_PATH, log_outputs, 'json', overwrite=True)

@DISCORD_CLIENT.event
async def on_ready():
    log_outputs = fileio.read_content(LOG_OUTPUT_PATH, 'json')
    message_defaults.update(log_outputs)
    await DISCORD_CLIENT.get_channel(CHANNEL_ID).send(
        content=message.format(**message_defaults), 
        file=discord.File(os.path.join(settings.LOGS_DIR, '{}.log'.format(settings.folder_name)))
    )
    await DISCORD_CLIENT.close()
    exit()
 

def notify(collect_ff=False):
    global message
    if collect_ff:
        message += """- User Followers Graph:
    - found `{found_followers}/{nodes_len}` nodes
    - found edges for `{len_followers_source}/{found_followers}` users
    - found `{len_followers}` edges
    """
    update_log_outputs()
    DISCORD_CLIENT.run(settings.DISCORD_TOKEN)
     

if __name__ == '__main__':
    update_log_outputs()
    print(log_outputs)
    DISCORD_CLIENT.run(settings.DISCORD_TOKEN)