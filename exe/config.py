import json

with open("config.json", "r") as file:
    config = json.load(file)

BASE_URL = config.get("BASE_URL")
PERSON = config.get("PERSON")
SCOPE_GROUPS = config.get("SCOPE_GROUPS")