from .client import SatyaClient

_client = None

def init(agent_name="default_agent", repo_path="."):
    global _client
    _client = SatyaClient(agent_name, repo_path)
    return _client

def log(message):
    if _client:
        _client.log(message)
    else:
        print(f"[Satya Not Initialized] {message}")

def create_task(title, description):
    if _client:
        return _client.create_task(title, description)
    return None

def update_task(task_id, status):
    if _client:
        return _client.update_task(task_id, status)
    return False

def scrape(url):
    if _client:
        return _client.scrape_url(url)
    return None
