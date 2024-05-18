import json

with open("config.json", "r") as file:
    config = json.load(file)

ADD_ZERO_TO_DNOM = config.get("ADD_ZERO_TO_DNOM", False)
MAX_THREADS = config.get("MAX_THREADS", 8)
BASE_URL = config.get("BASE_URL")
DEBUG_MODE = config.get("DEBUG_MODE", False)
MESSAGE_TEMPLATE = config.get("MESSAGE_TEMPLATE")
PERSON = config.get("PERSON")
SCOPE_GROUPS = config.get("SCOPE_GROUPS")