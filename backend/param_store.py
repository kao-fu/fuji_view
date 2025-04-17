# param_store.py

import json
from pathlib import Path
from typing import Any

# print current file path
PARAM_FILE = Path(__file__).parent / "config" / "params.json"

def load_params():
    with PARAM_FILE.open() as f:
        return json.load(f)

def save_params(params):
    with PARAM_FILE.open("w") as f:
        json.dump(params, f, indent=2)

def get_param(nested_key: str) -> Any:
    keys = nested_key.split(".")
    data = load_params()
    for key in keys:
        data = data[key]
    return data

def set_param(nested_key: str, value: Any):
    keys = nested_key.split(".")
    data = load_params()
    d = data
    for key in keys[:-1]:
        d = d[key]
    d[keys[-1]] = value
    save_params(data)
