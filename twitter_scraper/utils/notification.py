import os
import discord
import logging

from twitter_scraper import settings
from twitter_scraper import utils
from twitter_scraper.utils import fileio

discord.utils.setup_logging(level=logging.ERROR)

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = 1029494278751273011
LOG_OUTPUT_PATH = os.path.join(settings.LOGS_DIR, '{}.json'.format(settings.folder_name))

message = """twitter-scraper outputs:

- Debug = `{debug}`
- Initial baseline size: `{initial_baseline_len}`
- Final baseline size: `{final_baseline_len}`
- Number of Croatian users: `{cro_users_len}`
- User Followers Graph:
    - found `{found_followers}/{nodes_len}` nodes
    - found edges for `{len_followers_source}/{found_followers}` users
    - found `{len_followers}` edges
- User Mentions Graph:
    - found `{found_mentions}/{nodes_len}` nodes
    - found edges for `{len_mentions_source}/{found_mentions}` users
    - found `{len_mentions}` edges
- User Retweets Graph:
    - found `{found_retweets}/{nodes_len}` nodes
    - found edges for `{len_retweets_source}/{found_retweets}` users
    - found `{len_retweets}` edges
"""

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

def update_log_outputs():
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
    fileio.write_content(LOG_OUTPUT_PATH, log_outputs, 'json')

@client.event
async def on_ready():
    log_outputs = fileio.read_content(LOG_OUTPUT_PATH, file_type='json')
    await client.get_channel(CHANNEL_ID).send(
        content=message.format(**log_outputs), 
        file=discord.File(os.path.join(settings.LOGS_DIR, '{}.log'.format(settings.folder_name)))
    )
    await client.close()
    exit()
 

def notify():
    update_log_outputs()
    client.run(DISCORD_TOKEN)
     

if __name__ == '__main__':
    update_log_outputs()
    client.run(DISCORD_TOKEN)