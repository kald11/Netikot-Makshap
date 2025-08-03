import subprocess
import threading
import requests
from core.google_sheets import GoogleSheets
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


gs = GoogleSheets()
modem_df = gs.get_modem_data()
login_results = []
lock = threading.Lock()


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
    site_name = row.site.name
    status = "Failed"

    if is_ping_successful(ip):
        try:
            url = f'http://{ip}:{port}/api/login'
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            payload = {
                "username": "admin",
                "password": password
            }
            res = requests.post(url, headers=headers, json=payload, verify=False, timeout=10)

            if res.status_code == 200:
                status = "Success"
            elif res.status_code in [401, 403]:
                status = "Wrong Password"
        except Exception as e:
            print(e)

    row.site.modem.status_code = status



