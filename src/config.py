from fastapi.templating import Jinja2Templates

WORK_DIR = "src/"
TEMPLATES = Jinja2Templates(directory=f"{WORK_DIR}templates")
BASE_URL = "https://test.ubki.ua" # "https://secure.ubki.ua"
DOMAIN = "localhost"
