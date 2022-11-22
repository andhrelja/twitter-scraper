import os
import sys
import logging

from . import fileio
from twitter_scraper import settings


def get_logger(logger_name, **kwargs):
    path, logger_filename = os.path.split(logger_name)
    _, logger_module = os.path.split(path)
    logger_name = '{}.{}'.format(logger_module, logger_filename.replace('.py', ''))
    logger_filepath = os.path.join(settings.LOGS_DIR, '{}.log'.format(settings.folder_name))

    logging.basicConfig(
        format='[%(levelname)s] %(asctime)s %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.INFO,
        handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler(logger_filepath)],
        **kwargs
    )

    return logging.getLogger(logger_name)


def batches(obj, n=100):
    lst = list(obj)
    for i in range(0, len(lst), n):
        yield lst[i:i+n]


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


def read_directory_files(directory: str=None, read_fn: object=None, **kwargs):
    for folder_name in os.listdir(directory):
        folder_path = os.path.join(directory, folder_name)
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            yield read_fn(file_path, **kwargs)
