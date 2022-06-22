import os
import json
import random


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
INPUT_DIR = os.path.join(ROOT_DIR, 'data', 'input')
DEBUG_INPUT_DIR = os.path.join(ROOT_DIR, 'debug', 'input')

def sample_user_friends():
    
    return

def sample_baseline(sample_size=100):
    with open(os.path.join(INPUT_DIR, 'baseline-user-ids.json'), 'r', encoding='utf-8') as f:
        baseline_user_ids = json.load(f)
        print("Read {} baseline IDs".format(len(baseline_user_ids)))
    
    sample = set()
    while len(sample) < sample_size:
        sample.add(random.choice(baseline_user_ids))
    
    with open(os.path.join(DEBUG_INPUT_DIR, 'baseline-user-ids.json'), 'w', encoding='utf-8') as f:
        json.dump(list(sample), f, indent=2)
        print("Wrote {} baseline IDs".format(len(sample)))


if __name__ == '__main__':
    sample_baseline(10)