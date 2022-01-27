import os
import csv
import json


def write_content(path, content, file_type='csv'):
    if os.path.isfile(path):
        if file_type == 'csv':
            fieldnames = _get_content_fieldnames(content)
            _append_csv_content(path, content, fieldnames)
        elif file_type == 'json':
            _append_json_content(path, content)
    else:
        if file_type == 'csv':
            fieldnames = _get_content_fieldnames(content)
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
    existing_content = _read_json_content(path)
    if isinstance(content, list):
        content += existing_content
    elif isinstance(content, dict):
        content.update(existing_content)
    _write_json_content(path, content)


def _read_json_content(path, column=None, limit=None):
    if not os.path.isfile(path):
        return None
    with open(path, 'r', encoding='utf-8') as jsonfile:
        content = json.load(jsonfile)
    if column:
        return [item[column] for item in content[:limit]]
    else:
        if isinstance(content, list):
            return content[:limit]
        return content


def _read_csv_content(path, column, limit=None):
    if not os.path.isfile(path):
        return None
    with open(path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        content = list(reader)
    if column:
        return [item[column] for item in content[:limit]]
    else:
        return content[:limit]


def _get_content_fieldnames(content):
    fieldnames = []
    for item in content:
        if isinstance(item, dict):
            fieldnames.extend(item.keys())
        else:
            fieldnames.append('')
    return set(fieldnames)