import os
import json

def load_cases(raw_dir):
    for root, _, files in os.walk(raw_dir):
        for file in files:
            if file.endswith(".json"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    yield json.load(f)
