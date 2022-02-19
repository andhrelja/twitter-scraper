import os
import sys
import logging
import numpy as np
import pandas as pd

from . import fileio
from twitter_scraper import settings


def get_logger(logger_name, **kwargs):
    path, logger_filename = os.path.split(logger_name)
    _, logger_module = os.path.split(path)
    logger_name = '{}.{}'.format(logger_module, logger_filename.replace('.py', ''))
    logging.basicConfig(
        format='[%(levelname)s] %(asctime)s %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.INFO,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(os.path.join(settings.LOGS_DIR, '{}.log'.format(settings.folder_name)))
        ],
        **kwargs
    )

    return logging.getLogger(logger_name)


def batches(lst, n=100):
    batches = []
    for i in range(0, len(lst), n):
        batches.append(lst[i:i+n])
    return batches


def get_baseline_user_ids(processed_filepath=None):
    baseline_user_ids = set(fileio.read_content(settings.BASELINE_USER_IDS, 'json'))       
    missing_user_ids = set(fileio.read_content(settings.MISSING_USER_IDS, 'json'))
    
    baseline_user_ids.difference_update(missing_user_ids)
    if processed_filepath is None:
        return baseline_user_ids
    
    processed_user_ids = set(fileio.read_content(processed_filepath, 'json'))
    baseline_user_ids.difference_update(processed_user_ids)
    return baseline_user_ids

def mkdir(path):
    if not os.path.exists(path):
        os.mkdir(path)