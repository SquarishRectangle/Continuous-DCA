from pydantic import BaseModel
import json, os

class _Config(BaseModel):
    alpaca_auth: dict

s = {}
if os.path.exists('.secrets'):
    with open('.secrets', 'r') as f:
        s = json.load(f)
CFG = _Config(**s)
    