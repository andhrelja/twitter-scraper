import os

from .settings import BASELINE_USER_IDS

if not os.path.exists(BASELINE_USER_IDS):
    raise LookupError("Baseline user IDs was not found")