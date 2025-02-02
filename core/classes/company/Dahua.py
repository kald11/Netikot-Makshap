import hashlib
from datetime import datetime, timedelta
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
import pytz
import requests
import re
from core.classes.company.Company import Company
from utils.network_helpers import ping


class Dahua(Company):

    def __init__(self, site):
        super().__init__("Dahua", site=site)
        self.session_id = None
        self.media_find_object_id = None
        self.rpc_request_id = 0
        self._prefix_url = f"{self.site.prot}://{self.site.ip}:{self.site.nvr.port}"
        self._api_url = f"{self._prefix_url}/cgi-bin"

    def try_login(self):
        try:
            if self.flags["is_nvr_ping"]:
                login_url = f'http://{self.site.ip}:{self.site.nvr.port}/RPC2_Login'

                r = self._rpc_request(login_url, method="global.login",
                                      params={'userName': self.username, 'password': "",
                                              'clientType': "Dahua3.0-Web3.0"})
                if r is None:
                    print(f"Login failed for: {self.site}")
                    self.flags["login_ok"] = False
                    return False
                self.session_id = r["session"]
                realm = r['params']['realm']
                random = r['params']['random']

                # Password encryption algorithm
                # Reversed from rpcCore.getAuthByType
                pwd_phrase = f"{self.username}:{realm}:{self.password}".encode('utf-8')
                pwd_hash = hashlib.md5(pwd_phrase).hexdigest().upper()

                pass_phrase = f'{self.username}:{random}:{pwd_hash}'.encode('utf-8')
                pass_hash = hashlib.md5(pass_phrase).hexdigest().upper()

                # login2: the real login
                params = {'userName': self.username,
                          'password': pass_hash,
                          'clientType': "Dahua3.0-Web3.0",
                          'authorityType': "Default",
                          'passwordType': "Default"}
                r = self._rpc_request(login_url, method="global.login", params=params)

                self.flags["login_ok"] = bool(r['result'])
            else:
                self.flags["login_ok"] = False
        except Exception as e:
            print(f"Login failed with error: {e}")
            self.flags["login_ok"] = False

    def get_captures(self):
        count = 0
        try:
            if self.flags["login_ok"]:
                factory = self._create_factory()
                if factory != "":
                    if self._can_start_captures(factory):
                        count = self._get_amount_captures(factory)
                    self.captures["num_captures"] = str(count)
        except Exception as e:
            print("Failed to get captures with error: {}".format(e))

    # def get_camera_time(self):
    #     if self.flags["login_ok"]:
    #         url = f"/RPC2"
    #         r = self.rpc_request(url=url, method='global.getCurrentTime', params=None)
    #         if r['result']:
    #             current_time = r['params']['time']
    #             current_time = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S')
    #             return current_time
    #     return DEFAULT_DATETIME

    def _rpc_request(self, url, method, params, add_data={}):
        # Make a RPC request
        data = {'method': method, 'id': self.rpc_request_id, 'params': params} | add_data
        if self.session_id is not None:
            data['session'] = self.session_id

        self.rpc_request_id += 1
        r = self.session.post(url, json=data, timeout=self.timeout)

        if r.ok:
            return r.json()
        else:
            return None

    # Private functions for capturing
    def _create_factory(self):
        factory = ""
        r = requests.get(f'{self._api_url}/mediaFileFind.cgi?action=factory.create', auth=self.site.credentials,
                         timeout=self.timeout)
        if r.status_code == 200:
            factory = r.text.split('\r\n')[0].split('=')[1]
        return factory

    def _can_start_captures(self, factory):
        end_date, start_date = self._check_times()
        r = requests.get(
            f'{self._api_url}/mediaFileFind.cgi?action=findFile&object={factory}&condition.Channel={self.site.camera.number}&condition.StartTime={start_date}' +
            f'&condition.EndTime={end_date}&condition.Types[0]=jpg', auth=self.site.credentials,
            timeout=self.timeout)
        return "ok" in r.text.lower()

    def _get_amount_captures(self, factory):
        count = 0
        proceed = True
        while proceed:
            num_items = self._get_next_items(factory)
            if num_items > 0:
                count += num_items
            else:
                proceed = False
        return count

    def _get_next_items(self, factory):

        r = self.session.get(
            f"{self._api_url}/mediaFileFind.cgi?action=findNextFile&object={factory}&count=100",
            auth=self.site.credentials, timeout=self.timeout)

        if r.status_code == 200:
            if "error" not in r.text.lower():
                num_items = int(r.text.split('\r\n')[0].split('=')[1])
                return num_items
        else:
            print(f'Bug in get captures: {r.status_code},for site: {self.site}')
            r.raise_for_status()
        return 0

    def _create_media_find_object(self):
        r = self.session.get(f"{self._api_url}/mediaFileFind.cgi?action=factory.create",
                             auth=self.site.credentials, timeout=self.timeout)
        if r.ok:
            # self.media_find_object_id = r.text.split('=')[-1].strip("\x0a\x0d")
            data = r.text.split('\r\n')
            factory = data[0].split('=')[1]
            self.media_find_object_id = data

    def _check_times(self):
        current_time_israel = datetime.now(pytz.timezone("Asia/Jerusalem"))
        start_time = datetime.strftime(current_time_israel, '%Y-%m-%d %H:%M:%S')
        end_time = datetime.strftime(current_time_israel - timedelta(hours=4), '%Y-%m-%d %H:%M:%S')
        return start_time, end_time
