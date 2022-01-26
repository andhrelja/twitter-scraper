import os
import csv
import json


def write_content(path, content, file_type='csv', metadata={}):
    fieldnames = _get_content_fieldnames(content)
    for key, value in metadata:
        if key in fieldnames:
            key = key + '_custom'
        for i in range(len(content)):
            content[i][key] = value
    
    if os.path.isfile(path):
        if file_type == 'csv':
            _append_csv_content(path, content, fieldnames)
        elif file_type == 'json':
            _append_json_content(path, content)
    else:
        if file_type == 'csv':
            _write_csv_content(path, content, fieldnames)
        elif file_type == 'json':
            _write_json_content(path, content)


def read_content(path, file_type='csv'):
    if os.path.isfile(path):
        if file_type == 'csv':
            return _read_csv_content(path)
        elif file_type == 'json':
            return _read_json_content(path)
    else:
        raise FileNotFoundError("File '{}' not found".format(path))


def _write_csv_content(path, content, fieldnames):
    with open(path, 'w', encoding='utf-8', newline='') as csvfile:
        if isinstance(content, list):
            writer = csv.DictWriter(csvfile, fieldnames)
            writer.writeheader()
            writer.writerows(content)
        elif isinstance(content, dict):
            writer = csv.DictWriter(csvfile, content.keys())
            writer.writeheader()
            writer.writerow(content)


def _write_json_content(path, content):
    if isinstance(content, dict):
        content = [content]
    with open(path, 'w', encoding='utf-8') as jsonfile:
        json.dump(content, jsonfile, ensure_ascii=False, indent=2)


def _append_csv_content(path, content, fieldnames):
    with open(path, 'a', encoding='utf-8', newline='') as csvfile:
        if isinstance(content, list):
            writer = csv.DictWriter(csvfile, fieldnames)
            writer.writerows(content)
        elif isinstance(content, dict):
            writer = csv.DictWriter(csvfile, content.keys())
            writer.writerow(content)
        

def _append_json_content(path, content):
    if isinstance(content, dict):
        content = [content]
    with open(path, 'a', encoding='utf-8') as jsonfile:
        existing_content = json.load(jsonfile)
        content += existing_content
        json.dump(content, jsonfile, ensure_ascii=False, indent=2)


def _read_json_content(path, limit=None):
    if not os.path.isfile(path):
        return None
    with open(path, 'r', encoding='utf-8') as jsonfile:
        content = json.load(jsonfile)
        return content[:limit]


def _read_csv_content(path, limit=None):
    if not os.path.isfile(path):
        return None
    with open(path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        return list(reader)[:limit]


def _get_content_fieldnames(content):
    fieldnames = []
    for item in content:
        fieldnames.extend(item.keys())
    return set(fieldnames)