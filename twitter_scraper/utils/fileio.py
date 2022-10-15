import os
import csv
import json
import logging

path, logger_filename = os.path.split(__file__)
_, logger_module = os.path.split(path)
logger_name = '{}.{}'.format(logger_module, logger_filename.replace('.py', ''))
logger = logging.getLogger(logger_name)

def write_content(path, content, file_type='csv', fieldnames=None, overwrite=False, **kwargs):
    if os.path.isfile(path):
        if overwrite:
            if file_type == 'csv':
                _write_csv_content(path, content, fieldnames, **kwargs)
            elif file_type == 'json':
                _write_json_content(path, content, **kwargs)
        else:
            if file_type == 'csv':
                _append_csv_content(path, content, fieldnames, **kwargs)
            elif file_type == 'json':
                _append_json_content(path, content, **kwargs)
    else:
        if file_type == 'csv':
            _write_csv_content(path, content, fieldnames, **kwargs)
        elif file_type == 'json':
            _write_json_content(path, content, **kwargs)


def read_content(path, file_type='csv', column=None):
    if os.path.isfile(path):
        if file_type == 'csv':
            return _read_csv_content(path, column)
        elif file_type == 'json':
            return _read_json_content(path, column)
    else:
        return []


def _write_csv_content(path, content, fieldnames=None, **kwargs):
    with open(path, 'w', encoding='utf-8', newline='') as csvfile:
        if isinstance(content, list):
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, **kwargs)
            writer.writeheader()
            writer.writerows(content)
        elif isinstance(content, dict):
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, **kwargs)
            writer.writeheader()
            writer.writerow(content)


def _write_json_content(path, content, **kwargs):
    if 'indent' not in kwargs:
        kwargs['indent'] = 2
    if not isinstance(content, dict) and not isinstance(content, list):
        content = [content]
    with open(path, 'w', encoding='utf-8') as jsonfile:
        try:
            json.dump(content, jsonfile, ensure_ascii=False, **kwargs)
        except json.decoder.JSONDecodeError:
            logger.error("JSONDecodeError on '{}'".format(path))
            raise
        

def _append_csv_content(path, content, fieldnames=None, **kwargs):
    if content is None:
        logger.warning("No content to write: {}".format(path))
        return
    with open(path, 'a', encoding='utf-8', newline='') as csvfile:
        if isinstance(content, list):
            writer = csv.DictWriter(csvfile, fieldnames, **kwargs)
            writer.writerows(content)
        elif isinstance(content, dict):
            writer = csv.DictWriter(csvfile, content.keys(), **kwargs)
            writer.writerow(content)
        

def _append_json_content(path, content, **kwargs):
    if content is None:
        logger.warning("No content to write: {}".format(path))
        return
    if isinstance(content, str) or isinstance(content, int):
        content = [content]
    existing_content = _read_json_content(path)
    if isinstance(content, list):
        existing_content += content
    elif isinstance(content, dict):
        existing_content.update(content)
    _write_json_content(path, existing_content, **kwargs)


def _read_json_content(path, column=None):
    with open(path, 'r', encoding='utf-8') as jsonfile:
        try:
            content = json.load(jsonfile)
        except json.decoder.JSONDecodeError:
            logger.error("JSONDecodeError on '{}'".format(path))
            raise
    if column:
        return [item[column] for item in content]
    else:
        return content


def _read_csv_content(path, column):
    with open(path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        content = list(reader)
        if column:
            return [item[column] for item in content]
        else:
            return content
