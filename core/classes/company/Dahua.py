from core.classes.company.Company import Company
from utils.network_helpers import ping


class Dahua(Company):

    def __init__(self, site):
        super().__init__("Dahua", site=site)
        self.session_id = None
        self.media_find_object_id = None
        self.rpc_request_id = 0
    def try_login(self):
        if self.flags["is_nvr_ping"]:
            login_url = f'http://{self.site.ip}:{self.site.nvr.port}/RPC2_Login'

            r = self.rpc_request(login_url, method="global.login",
                                 params={'userName': self.username, 'password': "", 'clientType': "Dahua3.0-Web3.0"})

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
            r = self.rpc_request(url, method="global.login", params=params)

            self.flags["Login OK"] = bool(r['result'])
        else:
            self.flags["Login OK"] = None

        return self.flags["Login OK"]
    def get_captures(self):
        # Add the implementation here
        pass

    def get_camera_time(self):
        # Add the implementation here
        pass

    def _rpc_request(self, url, method, params, add_data={}):
        # Make a RPC request
        data = {'method': method, 'id': self.rpc_request_id, 'params': params} | add_data
        if self.session_id is not None:
            data['session'] = self.session_id

        self.rpc_request_id += 1
        r = self.session.post(url, json=data, timeout=DEFAULT_TIMEOUT)

        if r.ok:
            return r.json()
        else:
            return None
