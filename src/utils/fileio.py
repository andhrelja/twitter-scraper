import os
import csv
import json
import logging

logger = logging.getLogger(__file__)

def write_content(path, content, file_type='csv', fieldnames=None, overwrite=False):
    if os.path.isfile(path):
        if overwrite:
            if file_type == 'csv':
                _write_csv_content(path, content, fieldnames)
            elif file_type == 'json':
                _write_json_content(path, content)
        else:
            if file_type == 'csv':
                _append_csv_content(path, content, fieldnames)
            elif file_type == 'json':
                _append_json_content(path, content)
    else:
        if file_type == 'csv':
            _write_csv_content(path, content, fieldnames)
        elif file_type == 'json':
            _write_json_content(path, content)


def read_content(path, file_type='csv', column=None):
    if os.path.isfile(path):
        if file_type == 'csv':
            return _read_csv_content(path, column)
        elif file_type == 'json':
            return _read_json_content(path, column)
    else:
        return []


def _write_csv_content(path, content, fieldnames=None):
    with open(path, 'w', encoding='utf-8', newline='') as csvfile:
        if isinstance(content, list):
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(content)
        elif isinstance(content, dict):
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow(content)


def _write_json_content(path, content):
    if not isinstance(content, dict) and not isinstance(content, list):
        content = [content]
    with open(path, 'w', encoding='utf-8') as jsonfile:
        try:
            json.dump(content, jsonfile, ensure_ascii=False, indent=2)
        except json.decoder.JSONDecodeError:
            logger.error("JSONDecode error on {}.json".format(path))
        

def _append_csv_content(path, content, fieldnames=None):
    if content is None:
        logger.warning("No content to write: {}".format(path))
        return
    with open(path, 'a', encoding='utf-8', newline='') as csvfile:
        if isinstance(content, list):
            writer = csv.DictWriter(csvfile, fieldnames)
            writer.writerows(content)
        elif isinstance(content, dict):
            writer = csv.DictWriter(csvfile, content.keys())
            writer.writerow(content)
        

def _append_json_content(path, content):
    if content is None:
        logger.warning("No content to write: {}".format(path))
        return
    if isinstance(content, str) or isinstance(content, int):
        content = [content]
    existing_content = _read_json_content(path)
    if isinstance(content, list):
        content += existing_content
    elif isinstance(content, dict):
        content.update(existing_content)
    _write_json_content(path, content)


def _read_json_content(path, column=None):
    if not os.path.isfile(path):
        logger.warning("Empty File: {}".format(path))
        return []
    with open(path, 'r', encoding='utf-8') as jsonfile:
        content = json.load(jsonfile)
    if column:
        return [item[column] for item in content]
    else:
        return content


def _read_csv_content(path, column):
    if not os.path.isfile(path):
        logger.warning("Empty File: {}".format(path))
        return []
    with open(path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        content = list(reader)
        if column:
            return [item[column] for item in content]
        else:
            return content
