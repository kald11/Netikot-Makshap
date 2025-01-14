import uuid
from datetime import datetime, timedelta
from utils.utils import get_body_by_model
import requests
import xmltodict

from core.classes.company.Company import Company
from utils.network_helpers import ping
from utils.utils import ordered_dict_to_dict, datetime_format


class Hikvision(Company):

    def __init__(self, site):
        super().__init__("Hikvision", site=site)
        self._prefix_isapi = f"{self.site.prot}://{self.site.ip}:{self.site.nvr.port}/ISAPI"
        self._prefix_psia = f"{self.site.prot}://{self.site.ip}:{self.site.nvr.port}/PSIA"
        self.session = requests.Session()
        self.device_info = None
        self.timeout = self.site.config["project_setup"]["times"]["timeout_ping"]
        self.username = self.site.config["project_setup"]["username"]
        self.password = self.site.nvr.password
        self.model = None

    def try_login(self):
        if self.flags["is_nvr_ping"]:
            try:
                res = requests.get(f"{self._prefix_isapi}/System/status", auth=self.site.credentials,
                                   timeout=self.timeout)
                if res.ok:
                    self.flags["login_ok"] = True

                else:
                    res = requests.get(f"{self._prefix_psia}/System/status", auth=self.site.credentials,
                                       timeout=self.timeout)

                    if res.status_code == 401:  # old models don't support Digest Auth
                        new_credentials = (self.username, self.password)
                        res = requests.get(f"{self._prefix_psia}/System/status", auth=new_credentials,
                                           timeout=self.timeout)

                    self.flags["login_ok"] = res.ok

            except Exception as e:
                print("Failed to login with this error: {}".format(e))
                self.flags["login_ok"] = False
            finally:
                self._get_device_info()

        else:
            self.flags["login_ok"] = False

    def ping_camera(self):
        is_cam_ping = ping(self.site.prot, self.site.ip, self.site.camera.port)
        self.flags["is_cam_ping"] = is_cam_ping

    def ping_nvr(self):
        is_nvr_ping = ping(self.site.prot, self.site.ip, self.site.nvr.port)
        self.flags["is_nvr_ping"] = is_nvr_ping

    def get_camera_time(self):
        try:
            self._define_check_time()
            if self.device_info in [('TS-5012-F', 4), ("DS-TP50-12DT", 4)]:
                res = self.session.get(f"{self._prefix_psia}/System/time", auth=self.site.credentials,
                                       timeout=self.timeout)
                self.times["current_camera_time"] = self._extract_date(res)
            else:
                res = self.session.get(f"{self._prefix_isapi}/System/time", auth=self.site.credentials,
                                       timeout=self.timeout)
                self.times["current_camera_time"] = self._extract_date(res)
            self._compare_between_dates()
        except Exception as e:
            # TODO: handle timeout exception exception
            pass

    def _get_device_info(self):
        if self.flags["login_ok"]:
            try:
                r = self.session.get(f"{self._prefix_isapi}/System/deviceInfo", auth=self.site.credentials,
                                     timeout=self.timeout)
                if r.ok:
                    r = ordered_dict_to_dict(xmltodict.parse(r.text))["DeviceInfo"]
                    self.device_info = (r["model"], int(r["firmwareVersion"][1:].split('.')[0]))
                else:
                    r = self.session.get(f"{self._prefix_psia}/system/deviceInfo", auth=self.site.credentials,
                                         timeout=self.timeout)
                    if r.ok:
                        r = ordered_dict_to_dict(xmltodict.parse(r.text))["DeviceInfo"]
                        self.device_info = (r["model"], int(r["firmwareVersion"][1:].split('.')[0]))

                if self.device_info in [('TS-5012-F', 4)]:  # some models don't support Digest Auth
                    self.site.credentials = (self.site.config["project_setup"]["username"], self.site.nvr.password)
                self._get_model()

            except Exception as e:
                print("Error getting device information, error {}".format(e))

    def _get_model(self):
        match self.device_info:
            case ("DS-TP50-16E", 4) | ("DS-TP50-16E", 5) | ("DS-TP50-12DT", 4) | ("DS-TP50-12DT", 5) | ("DS-TP50-04H",
                                                                                                        5) | (
                     "DS-TP50-08H", 5):
                # model index 1
                self.model = 1

            case ("DS-7604NI-E1/A", 3) | ("DS-7608NI-G2/4P", 3) | ("DS-7608NI-E2/A", 3) | ("DS-M5504HNI", 5) | (
                "DS-7604NI-K1", 4) | ("DS-7604NI-K1(B)", 3):
                # model index 2
                self.model = 2

            case ("DS-TP50-12DT", 4) | ("TS-5012-F", 4):
                # model index 3
                self.model = 3

            case _:
                print("Unknown device:")
                print(self.site)

    def _define_check_time(self):
        format = self.site.config["project_setup"]["format_datetime"]
        current_time = datetime.now().strftime(format)
        self.times["check_time"] = current_time

    def _extract_date(self, response):
        if response.status_code != 200:
            return ""
        data = response.text
        current_time_camera = ordered_dict_to_dict(xmltodict.parse(data))["Time"]["localTime"].replace('T', ' ')[:-6]
        return current_time_camera

    def _compare_between_dates(self):
        if self.times["current_camera_time"] == "" or self.times["check_time"] == "":
            return
        time_diff = self.site.config["project_setup"]["times"]["check_minutes_diff"]
        camera_time = datetime_format(self.times["current_camera_time"])
        current_time = datetime_format(self.times["check_time"])
        diff = abs(camera_time - current_time)
        self.times["is_synchronized"] = diff < timedelta(minutes=time_diff)

    def get_captures(self):
        # LPR check
        match self.model:
            case 1:
                self._get_data_model_1()
            case 2:
                self._get_data_model_2()
            case 3:
                self._get_data_model_3()

    def check_unknowns(self):
        self.get_captures()
        unkonwn_counter = 0
        if self.captures["num_captures"] != "" and self.model == 1:
            for index in range(0, int(self.captures["num_captures"]) + 1, 100):
                xml_body = self._get_request_params(index, self.model)
                response = self.session.post(f"{self._prefix_isapi}/Traffic/ContentMgmt/dataOperation",
                                             auth=self.site.credentials,
                                             data=xml_body,
                                             timeout=self.timeout)

                if response.ok:
                    unkonwn_counter += len([element for element in
                                            ordered_dict_to_dict(xmltodict.parse(response.text))['TrafficSearchResult'][
                                                'matchList']['matchElement'] if
                                            element["trafficData"]["plate"] == "unknown"])
            self.unknown_percent_morning = unkonwn_counter/self.captures["num_captures"]

    def _get_data_model_1(self):
        try:
            xml_body = self._get_request_params(index=0, model=1)

            response = self.session.post(f"{self._prefix_isapi}/Traffic/ContentMgmt/dataOperation",
                                         auth=self.site.credentials,
                                         data=xml_body,
                                         timeout=self.timeout)

            if response.ok:
                self._parse_data_response(response)
            # elif response.status_code == 503:
            #     print(self.site)
            #     print(response.text)
        except Exception as e:
            print(e)

    def _get_data_model_2(self):
        xml_body = self._get_request_params(index=0, model=2)
        response = self.session.post(f"{self._prefix_isapi}/ContentMgmt/search", auth=self.site.credentials,
                                     data=xml_body,
                                     timeout=self.timeout)

        if response.ok:
            x = 1
        # TODO: Add logic when add more cameras

    def _get_data_model_3(self):
        xml_body = self._get_request_params(index=0, model=4)
        response = self.session.post(f"{self._prefix_psia}/Custom/SelfExt/ContentMgmt/Traffic/Search",
                                     auth=self.site.credentials,
                                     data=xml_body,
                                     timeout=self.timeout)
        if response.ok:
            x = 1

    def _get_request_params(self, index, model,type =None):
        start_time = ""
        format = "%Y-%m-%dT%H:%M:%SZ"
        end_time = datetime.utcnow()
        if type is None:
            start_time = end_time - timedelta(hours=3)
            start_time = start_time.strftime(format)
            end_time = end_time.strftime(format)

        elif type == 'morning':
            start_time = '2025-01-13T10:00:00Z'
            end_time = '2025-01-13T11:00:00Z'

        elif  type == 'night':
            start_time = '2025-01-13T22:00:00Z'
            end_time = '2025-01-13T23:00:00Z'

        data_request_xml = get_body_by_model(model=model, index=index, start_time=start_time, end_time=end_time,
                                             camera_number=self.site.camera.number)
        return data_request_xml

    def _parse_data_response(self, response):
        data = ordered_dict_to_dict(xmltodict.parse(response.text))["TrafficSearchResult"]
        total_matches = data["totalMatches"]
        self.captures["num_captures"] = total_matches
