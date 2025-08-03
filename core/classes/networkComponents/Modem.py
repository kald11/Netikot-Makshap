import subprocess

import requests

from core.classes.networkComponents.NetworkComponent import NetworkComponent
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Modem(NetworkComponent):
    def __init__(self, port, password):
        super().__init__(port, password)
        self.status_code = ""


    def __str__(self):
        return f"Network Video Recorder (NVR) on port {self.port} with password {self.password}"

def is_ping_successful(ip):
    try:
        result = subprocess.run(['ping', '-n', '1', ip], capture_output=True, text=True, timeout=2)
        return 'TTL=' in result.stdout
    except Exception:
        return False


def try_login_modem_worker(row):
    ip = str(row.site.ip)
    port = str(row.site.modem.port)
    password = row.site.modem.password
    status = "Failed"

    if not is_ping_successful(ip):
        row.site.modem.status_code = status
        return

    if "בזק" in port:
        status = "Success"
        return

    for protocol in ["http", "https"]:
        try:
            url = f'{protocol}://{ip}:{port}/api/login'
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            payload = {
                "username": "admin",
                "password": password
            }
            res = requests.post(url, headers=headers, json=payload, verify=False, timeout=5)

            if res.status_code == 200:
                status = "Success"
            elif res.status_code in [401, 403]:
                status = "Wrong Password"
            else:
                status = f"HTTP {res.status_code}"

            break  # Exit loop if we got a response
        except requests.exceptions.ConnectionError:
            continue
        except Exception as e:
            print(f"{e}")
            break

    row.site.modem.status_code = status
