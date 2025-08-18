import hashlib
from datetime import datetime, timedelta, time

import pytz
import requests

from core.classes.company.Company import Company

from config.settings import Config
from exceptions.exceptions import handle_exception
import re


class Dahua(Company):

    def __init__(self, site, index, unknown_morning, unknown_night):
        self.config = Config().get_config()
        super().__init__("Dahua", site=site, index=index, unknown_morning=unknown_morning, unknown_night=unknown_night)
        self.session_id = {"camera": None, "nvr": None}
        self.rpc_request_id = 0
        self._api_url = f"{self.site.prot}://{self.site.ip}:{self.site.nvr.port}/cgi-bin"

    def try_login(self, type="nvr"):
        attr = f"login_{'camera_' if type == 'camera' else ''}ok"
        try:
            if self.flags[f"is_{type}_ping"]:
                login_url = f'http://{self.site.ip}:{getattr(self.site, type).port}/RPC2_Login'
                r = self._rpc_request(login_url, method="global.login", type=type,
                                      params={'userName': self.username, 'password': "",
                                              'clientType': "Dahua3.0-Web3.0"})
                if r is None:
                    print(f"Login failed for: {self.site}")
                    self.flags[attr] = False
                    return False
                self.session_id[type] = r["session"]
                pass_hash = self._encrypt_password(r)
                params = self._get_login_params(pass_hash)
                r = self._rpc_request(login_url, method="global.login", type=type, params=params)
                self.flags[attr] = bool(r['result'])
            else:
                self.flags[attr] = False
        except Exception as e:
            handle_exception(e, self, "login")
            self.flags[attr] = False

    def get_captures(self, type=None):
        try:
            if self.flags["login_ok"]:
                factory = self._create_factory()
                if factory != "":

                    if type == "24_hours" and self._can_start_captures(factory, last_x_hours=24):
                        self.captures["num_captures_per_day"] = str(self._get_amount_captures(factory))

                    elif self._can_start_captures(factory, last_x_hours=4):
                        self.captures["num_captures"] = str(self._get_amount_captures(factory))
        except Exception as e:
            handle_exception(e, self, "captures")

    def check_live(self):
        pass

    def get_camera_time(self, type="nvr"):
        try:
            match type:
                case "camera":
                    if not self.flags["login_camera_ok"]:
                        self.times['is_camera_synchronized'] = "אין אפשרות להיכנס לcamera"
                        self.define_check_time()
                        return
                case "nvr":
                    if not self.flags["login_ok"]:
                        self.times['is_nvr_synchronized'] = "אין אפשרות להיכנס לnvr"
                        self.define_check_time()
                        return
            #if self.flags[f"login{'_camera' if type == 'camera' else ''}_ok"]:
            url = f'{self.site.prot}://{self.site.ip}:{getattr(self.site, type).port}/RPC2'
            r, status_code = self._rpc_request(url=url, method='global.getCurrentTime', type=type, params=None)

            if r.status_code != 200:
                match status_code:
                    case 401:
                        self.times[f"is_{type}_synchronized"] = f"אין הרשאה - שם משתמש או סיסמה שגויים ({type})"
                    case 403:
                        self.times[f"is_{type}_synchronized"] = f"אין הרשאה לגשת למשאב זה ({type})"
                    case 404:
                        self.times[f"is_{type}_synchronized"] = "כתובת לא קיימת"
                    case _:
                        self.times[f"is_{type}_synchronized"] = f'{status_code} unknown error'
            elif r.status_code == 200 and ['result']:
                self._parse_current_time(r, type)

        except Exception as e:
            self.times[f"is_{type}_synchronized"] = f'אין אפשרות להיכנס ל{type}'
            handle_exception(e, self, "camera time")

    def check_playback(self):
        try:
            end_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            start_time = (datetime.utcnow() - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
            factory = self._create_factory()
            self._request_file_list(factory, start_time, end_time)
            response = self._fetch_next_files(factory)
            if response and response.status_code == 200:
                self._has_playback(response.text)

        except Exception as e:
            handle_exception(e, self, "playback")

    def _rpc_request(self, url, method, params, type="nvr", add_data={}):
        # Make a RPC request
        data = {'method': method, 'id': self.rpc_request_id, 'params': params} | add_data

        if self.session_id[type] is not None:
            data['session'] = self.session_id[type]

        self.rpc_request_id += 1  # Fixed indentation
        r = self.session.post(url, json=data, timeout=self.timeout)  # Fixed indentation

        if r.ok:
            return r.json(), r.status_code
        else:
            return r.status_code

    # Private functions for capturing
    def _create_factory(self):
        factory = ""
        r = requests.get(f'{self._api_url}/mediaFileFind.cgi?action=factory.create', auth=self.site.credentials,
                         timeout=self.timeout)
        if r.status_code == 200:
            factory = r.text.split('\r\n')[0].split('=')[1]
        return factory

    def _can_start_captures(self, factory, last_x_hours, *args):
        end_date, start_date = self._check_times_captures(None if not args else args[0],
                                                          check_last_x_hours=last_x_hours)
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

    def _check_times_captures(self, *args, check_last_x_hours):
        current_time_israel = datetime.now(pytz.timezone("Asia/Jerusalem"))
        if not args[0]:
            end_time = datetime.strftime(current_time_israel, self.config["project_setup"]["format_datetime"])
            start_time = datetime.strftime(current_time_israel - timedelta(hours=check_last_x_hours),
                                           self.config["project_setup"]["format_datetime"])
        else:
            time_period = args[0]
            end_time, start_time = self._get_times_unknowns(time_period)
        return end_time, start_time

    def _get_times_unknowns(self, time_period):
        yesterday = datetime.now().date() - timedelta(days=1)
        if time_period == "morning":
            start_date = datetime.combine(yesterday, time(10, 0, 0))
            end_date = datetime.combine(yesterday, time(11, 0, 0))
        elif time_period == "night":
            start_date = datetime.combine(yesterday, time(22, 0, 0))
            end_date = datetime.combine(yesterday, time(23, 0, 0))
        return end_date, start_date

    def _parse_current_time(self, r, type):
        current_time = r['params']['time']
        self.times[f"current_{type}_time"] = current_time
        self.define_check_time()
        self.compare_between_dates(type)

    def check_unknowns(self, time_period):
        try:
            result = "0/0"
            total_captures, unknown_captures = self._get_captures_by_time(time_period)

            if total_captures > 0:
                percentage = round((unknown_captures / total_captures) * 100, 2)
                result = f"{unknown_captures} / {total_captures} => {percentage}%"

            self.unknowns[time_period] = result
        except Exception as e:
            handle_exception(e, self, "unknowns")

    def _get_captures_by_time(self, time_period):
        captures, unknown = 0, 0
        if self.flags["login_ok"]:
            factory = self._create_factory()
            if factory and self._can_start_captures(factory, time_period):
                return self._get_unknowns_by_time(factory)
        return captures, unknown

    def _get_unknowns_by_time(self, factory):
        total, unknown_plates = 0, 0
        while True:
            captures, unknown = self._get_next_items_by_time(factory)
            if captures == 0:
                break
            total += captures
            unknown_plates += unknown
        return total, unknown_plates

    def _get_next_items_by_time(self, factory):
        try:
            r = self.session.get(
                f"{self._api_url}/mediaFileFind.cgi?action=findNextFile&object={factory}&count=100",
                auth=self.site.credentials, timeout=self.timeout
            )

            if r.status_code != 200 or "error" in r.text.lower():
                print(f'API Error: {r.status_code}, Response: {r.text}')
                return 0, 0
            plate_numbers = re.findall(r"Summary\.TrafficCar\.PlateNumber=(.*)", r.text)
            total_plate_numbers = len(plate_numbers)
            empty_count = len([plate for plate in plate_numbers if plate == "\r"])

            return total_plate_numbers, empty_count

        except Exception as e:
            handle_exception(e, "unknowns")
            return None

    def _encrypt_password(self, r):
        realm = r['params']['realm']
        random = r['params']['random']
        pwd_phrase = f"{self.username}:{realm}:{self.camera_password}".encode('utf-8')
        pwd_hash = hashlib.md5(pwd_phrase).hexdigest().upper()
        pass_phrase = f'{self.username}:{random}:{pwd_hash}'.encode('utf-8')
        pass_hash = hashlib.md5(pass_phrase).hexdigest().upper()
        return pass_hash

    def _get_login_params(self, pass_hash):
        return {'userName': self.username,
                'password': pass_hash,
                'clientType': "Dahua3.0-Web3.0",
                'authorityType': "Default",
                'passwordType': "Default"}

    def _request_file_list(self, factory, start_time, end_time):
        url = (f"http://{self.site.ip}:{self.site.nvr.port}/cgi-bin/mediaFileFind.cgi"
               f"?action=findFile&object={factory}&condition.Channel={self.site.camera.number}"
               f"&condition.StartTime={start_time}&condition.EndTime={end_time}"
               f"&condition.Types[0]=dav0&condition.Types[1]=mp4")
        self.session.get(url, auth=self.site.credentials, timeout=self.timeout)

    def _fetch_next_files(self, factory):
        url = (f"http://{self.site.ip}:{self.site.nvr.port}/cgi-bin/mediaFileFind.cgi"
               f"?action=findNextFile&object={factory}&count=100")
        return self.session.get(url, auth=self.site.credentials, timeout=self.timeout)

    def _has_playback(self, response_text):
        self.captures["playback"] = "V" if "found=" in response_text and int(
            response_text.split("found=")[1].split("\n")[0]) > 0 else "X"
