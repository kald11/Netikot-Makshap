import requests

from config.settings import Config


def ping(prot, ip, port):
    try:
        config = Config().get_config()
        prefix = 'http://' if prot.lower() == 'http' else 'https://'
        url = f"{prefix}{ip}:{port}"
        response = requests.get(url, timeout=config['project_setup']["times"]["timeout_ping"])
        return response.status_code == 200
    except Exception as e:
        print(f"An error occurred: {e}")
        print(f"For IP: {ip}:{port}")
        return False
