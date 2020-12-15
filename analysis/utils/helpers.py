import json
import os

league_id = 189331

def load_cookies(project_root: str) -> dict:
    cookies_path = os.path.join(project_root, "data", "espn_keys.json")
    with open(cookies_path, "r") as file_obj:
        cookies = json.load(file_obj)
    return cookies
