import uuid
from datetime import datetime, timedelta

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

    def try_login(self):
        if self.flags["is_nvr_ping"]:
            try:
                res = requests.get(f"{self._prefix_isapi}/system/status", auth=self.site.credentials, timeout=self.timeout)
                if res.ok:
                    self.flags["login_ok"] = True

                else:
                    res = requests.get(f"{self._prefix_psia}/system/status", auth=self.site.credentials, timeout=self.timeout)

                    if res.status_code == 401:  # old models don't support Digest Auth
                        new_credentials = (self.username, self.password)
                        res = requests.get(f"{self._prefix_psia}/system/status", auth=new_credentials, timeout=self.timeout)

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
                res = self.session.get(f"{self._prefix_psia}/system/time", auth=self.site.credentials,
                                       timeout=self.timeout)
                self.times["current_camera_time"] = self._extract_date(res)
            else:
                res = self.session.get(f"{self._prefix_isapi}/system/time", auth=self.site.credentials,
                                       timeout=self.timeout)
                self.times["current_camera_time"] = self._extract_date(res)
            self._compare_between_dates()
        except Exception as e:
            # TODO: handle timeout exception exception
            pass

    def _get_device_info(self):
        if self.flags["login_ok"]:
            try:
                r = self.session.get(f"{self._prefix_isapi}/system/deviceInfo", auth=self.site.credentials,
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
            except Exception as e:
                print("Error getting device information, error {}".format(e))

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
        if self.device_info in [("DS-TP50-16E", 4), ("DS-TP50-16E", 5), ("DS-TP50-12DT", 4),
                                ('DS-TP50-12DT', 5), ('DS-TP50-04H',
                                                      5), ('DS-TP50-08H', 5)]:  # model index 1
            try:
                response = self._get_data_model_1(index=0,)

            except:
                x=1

    def _get_data_model_1(self, index):
        start_time= "2025-01-09T00:00:00Z"
        end_time = "2025-01-09T23:59:59Z"
        data_request_xml_base = f'''
                            <DataOperation>
                                <operationType>search</operationType>
                                <searchCond>
                                    <searchID>{str(uuid.uuid4())}</searchID>
                                    <timeSpanList>
                                        <timeSpan>
                                            <startTime>{start_time}</startTime>
                                            <endTime>{end_time}</endTime>
                                        </timeSpan>
                                    </timeSpanList>
                                    <criteria>
                                        <dataType>0</dataType>
                                        <channel>{self.site.camera.number}</channel>
                                        <violationType>0</violationType>
                                        <surveilType>0</surveilType>
                                        <analysised>true</analysised>
                                    </criteria>
                                    <searchResultPosition>{index}</searchResultPosition>                                    
                                </searchCond>
                            </DataOperation>'''

        data = self.session.post(f"{self._prefix_isapi}/Traffic/ContentMgmt/dataOperation",
                                 auth=self.site.credentials,
                                 data=data_request_xml_base,
                                 timeout=self.timeout)

        if data.ok:
            x=1
            # data = ordered_dict_to_dict(xmltodict.parse(data.text))["TrafficSearchResult"]
            # pic_amount = int(self.get_amount_pictures(cam_number=cam_id, model=1, data=data))
            # if int(data["numOfMatches"]) > 0:
            #     if len(data['matchList']['matchElement']) > 1:
            #         return data['matchList']['matchElement'][-1]['trafficData']['captureTime'], data[
            #             'totalMatches'], pic_amount
            #     return data['matchList']['matchElement']['trafficData']['captureTime'], data['totalMatches']

        return "", '', 0
