import os
import random
import pandas as pd
from typing import List

from utils import fileio

from twitter_scraper.settings import ROOT_DIR

INPUT_DIR = os.path.join(ROOT_DIR, 'input')
DEBUG_INPUT_DIR = os.path.join(ROOT_DIR, 'debug', 'input')

def sample_user_friends() -> List[list]:
    
    return

def sample_baseline(sample_size=10) -> List[list]:
    baseline_user_ids = fileio.read_content(os.path.join(INPUT_DIR, 'baseline-user-ids.json'), 'json')
    sample = set()
    while len(sample) < sample_size:
        sample.add(random.choice(baseline_user_ids))
    fileio.write_content(os.path.join(DEBUG_INPUT_DIR, 'baseline-user-ids.json'), list(sample), 'json')


if __name__ == '__main__':
    sample_baseline(10)