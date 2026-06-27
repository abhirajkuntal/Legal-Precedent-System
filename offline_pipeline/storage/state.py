# offline_pipeline/storage/state.py

import json
from pathlib import Path

STATE_FILE = Path("data/artifacts/state.json")

def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"last_case": 0}

def save_state(state):
    STATE_FILE.write_text(json.dumps(state))
