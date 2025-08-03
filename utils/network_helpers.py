import requests
from urllib3.exceptions import ReadTimeoutError

from config.settings import Config
from exceptions import ConnectionErrorException, TimeoutErrorException, ReadTimeoutErrorException
from exceptions.exceptions import handle_exception


def ping(device, comp):
    site = device.site
    try:
        config = Config().get_config()
        prefix = 'http://' if site.prot.lower() == 'http' else 'https://'

        if comp == "camera":
            url = f"{prefix}{site.ip}:{site.camera.port}"
        else:
            url = f"{prefix}{site.ip}:{site.nvr.port}"

        response = requests.get(url, timeout=config['project_setup']["times"]["timeout_ping"])
        return response.status_code == 200

    except Exception as e:
        handle_exception(e, device, "ping")
