from datetime import datetime, timedelta
from ftplib import FTP
import xml.etree.ElementTree as ET

import cv2
import pytz
import requests
from exceptions.exceptions import handle_exception
from utils.utils import get_body_by_model, get_captures_times
import xmltodict
from core.classes.company.Company import Company
from utils.utils import parse_text_to_dict, datetime_format
import json
import re

from config.settings import Config


class Hikvision(Company):

    def __init__(self, site, index, unknown_morning, unknown_night):
        super().__init__("Hikvision", site=site, index=index, unknown_morning=unknown_morning,
                         unknown_night=unknown_night)
        self._prefix_isapi = f"{self.site.prot}://{self.site.ip}:{self.site.nvr.port}/ISAPI"
        self._prefix_psia = f"{self.site.prot}://{self.site.ip}:{self.site.nvr.port}/PSIA"

        self.device_info = None
        self.model = None
        self.playback_channel = None

        self.config = Config().get_config()

    def try_login(self, type):
        attr = f"login_{'camera_' if type == 'camera' else ''}ok"
        if self.flags[f"is_{type}_ping"]:

            prefix_isapi = f"{self.site.prot}://{self.site.ip}:{getattr(self.site, type).port}/ISAPI"
            prefix_psia = f"{self.site.prot}://{self.site.ip}:{getattr(self.site, type).port}/PSIA"
            creds = self.site.credentials_camera if type == "camera" else self.site.credentials

            try:
                res = requests.get(f"{prefix_isapi}/System/status", auth=creds,
                                   timeout=self.timeout)
                self.check_wrong_password(res, type)
                if res.ok:
                    self.flags[attr] = True
                else:
                    creds = (self.username, self.camera_password if type == "camera" else self.site.nvr.password)
                    res = requests.get(f"{prefix_psia}/System/status", auth=creds
                                       ,
                                       timeout=self.timeout)
                    self.check_wrong_password(res, type)

                    self.flags[attr] = res.ok
            except Exception as e:
                handle_exception(e, self, "login")
                self.flags[attr] = False
            finally:
                self.get_device_info()

        else:
            self.flags[attr] = False

    def check_wrong_password(self, res, type):
        if res.status_code == 401:
            handle_exception(f"Wrong password ", self, "login", type)

    def get_camera_time(self, type="nvr"):
        try:
            self.define_check_time()
            credentials = self.site.credentials
            prefix_isapi = f"{self.site.prot}://{self.site.ip}:{getattr(self.site, type).port}/ISAPI"
            prefix_psia = f"{self.site.prot}://{self.site.ip}:{getattr(self.site, type).port}/PSIA"
            if self.device_info in [('TS-5012-F', 4), ("DS-TP50-12DT", 4)]:
                res = self.session.get(f"{prefix_psia}/System/time", auth=credentials, timeout=self.timeout)
            else:
                res = self.session.get(f"{prefix_isapi}/System/time", auth=credentials, timeout=self.timeout)

            self.handle_time_res(type, res)

        except Exception as e:
            self.times[f"is_{type}_synchronized"] = f'אין אפשרות להיכנס ל{type}'
            handle_exception(e, self, f'{type} time error')

    def handle_time_res(self, type, res):
        try:
            if res.status_code != 200:
                match res.status_code:
                    case 401:
                        self.times[f"is_{type}_synchronized"] = f"אין הרשאה - שם משתמש או סיסמה שגויים ({type})"
                    case 403:
                        self.times[f"is_{type}_synchronized"] = f"אין הרשאה לגשת למשאב זה ({type})"
                    case 404:
                        self.times[f"is_{type}_synchronized"] = "כתובת לא קיימת"
                    case _:
                        self.times[f"is_{type}_synchronized"] = f'{res.status_code} unknown error'
            else:
                self.times[f"current_{type}_time"] = self._extract_date(res)
                self.compare_between_dates(type)
        except Exception as e:
            handle_exception(e, self, f'{type} time error')

    def get_device_info(self):
        if self.flags["login_ok"]:
            try:
                r = self.session.get(f"{self._prefix_isapi}/System/deviceInfo", auth=self.site.credentials,
                                     timeout=self.timeout)
                if r.ok:
                    r = parse_text_to_dict(xmltodict.parse(r.text))["DeviceInfo"]
                    self.device_info = (r["model"], int(r["firmwareVersion"][1:].split('.')[0]))
                else:
                    r = self.session.get(f"{self._prefix_psia}/system/deviceInfo", auth=self.site.credentials,
                                         timeout=self.timeout)
                    if r.ok:
                        r = parse_text_to_dict(xmltodict.parse(r.text))["DeviceInfo"]
                        self.device_info = (r["model"], int(r["firmwareVersion"][1:].split('.')[0]))

                if self.device_info in [('TS-5012-F', 4)]:  # some models don't support Digest Auth
                    self.site.credentials = (self.site.config["project_setup"]["username"], self.site.nvr.password)
                self._get_model()

            except Exception as e:
                handle_exception(e, self, "device info")

    def _get_model(self):
        match self.device_info:
            case ("DS-TP50-16E", 4) | ("DS-TP50-16E", 5) | ("DS-TP50-12DT", 4) | ("DS-TP50-12DT", 5) | ("DS-TP50-04H",
                                                                                                        5) | (
                     "DS-TP50-08H", 5):
                # model index 1
                self.model = 1

            case ("DS-7604NI-E1/A", 3) | ("DS-7608NI-G2/4P", 3) | ("DS-7608NI-E2/A", 3) | ("DS-M5504HNI", 5) | (
                "DS-7604NI-K1", 4) | ("DS-7604NI-K1(B)", 3) | ('DS-7604NXI-K1', 4) | ('DS-7604NI-E1/A', 3) | (
                     'DS-7608NXI-K2', 4):
                # model index 2
                self.model = 2

            case ("DS-TP50-12DT", 4) | ("TS-5012-F", 4):
                # model index 3
                self.model = 3

            case _:
                if self.site.camera_id != "אווירה":
                    print("Unknown device:")
                    print(self.site)
                    print(self.device_info)
                else:
                    self.model = 2

    def _extract_date(self, response):
        if response.status_code != 200:
            return ""
        data = response.text
        current_time_camera = parse_text_to_dict(xmltodict.parse(data))["Time"]["localTime"].replace('T', ' ')[:-6]
        return current_time_camera

    def get_captures(self, type=None):
        try:
            match self.model:
                case 1:
                    self._get_data_model_1(type)
                case 2:
                    self._get_data_model_2(type)
                case 3:
                    self._get_data_model_3(type)
        except Exception as e:
            handle_exception(e, self, "captures")

    def check_unknowns(self, time_period):
        """
        Check unknown plates for the specified time period ('morning' or 'night').
        """
        try:
            if self.model == 1:
                total_matches = self._get_total_matches(time_period)
                if total_matches > 1:
                    unknown_count = self._count_unknown_plates(total_matches, time_period)
                    result = f"{unknown_count} / {total_matches} => {round(unknown_count / total_matches, 2) * 100}%"
                    self.unknowns[time_period] = result
                elif total_matches <= 1:
                    self.unknowns[time_period] = "0/0"
        except Exception as e:
            handle_exception(e, self, "unknowns")

    def check_live(self):
        try:
            prefix = f"rtsp://admin:{self.site.nvr.password}@{self.site.ip}"
            stream = cv2.VideoCapture(
                f'{prefix}:554/Streaming/channels/{self.site.camera.number}02')
            if not stream.isOpened():
                stream = cv2.VideoCapture(
                    f'{prefix}:554/PSIA/Streaming/channels/{self.site.camera.number}02')
                if not stream.isOpened():
                    self.live_view = False
                    stream.release()
                    return
            self.live_view = True
            stream.release()
        except Exception as e:
            handle_exception(e, self, "live view")

    def check_playback(self):
        try:
            payload = self._payload_playback()
            r = self.session.post(f'{self._prefix_isapi}/ContentMgmt/search', auth=self.site.credentials, data=payload,
                                  timeout=self.timeout)
            if r.status_code == 200:
                self._has_playback(r.text)
        except Exception as e:
            handle_exception(e, self, "playback")

    def _get_total_matches(self, time_period):
        request_body = self._build_request_body(0, self.model, time_period)
        response = self._send_captures_request(request_body)
        if not response.ok:
            request_body = self._build_request_body(0, self.model, time_period, True)
            response = self._send_captures_request(request_body)
        return int(self._parse_total_matches(response))

    def _count_unknown_plates(self, total_matches, time_period):
        unknown_count = 0
        for offset in range(0, total_matches + 1, 100):
            request_body = self._build_request_body(offset, self.model, time_period)
            response = self._send_captures_request(request_body)
            if not response.ok:
                request_body = self._build_request_body(0, self.model, time_period, True)
                response = self._send_captures_request(request_body)
            unknown_count += self._count_unknown_in_response(response)
        return unknown_count

    def _send_captures_request(self, request_body):
        return self.session.post(
            f"{self._prefix_isapi}/Traffic/ContentMgmt/dataOperation",
            auth=self.site.credentials,
            data=request_body,
            timeout=self.timeout,
        )

    def _parse_total_matches(self, response):
        return parse_text_to_dict(xmltodict.parse(response.text))['TrafficSearchResult']['totalMatches']

    def _count_unknown_in_response(self, response):
        match_list = parse_text_to_dict(xmltodict.parse(response.text))['TrafficSearchResult']['matchList'][
            'matchElement']
        return len([match for match in match_list if match["trafficData"]["plate"] == "unknown"])

    def _build_request_body(self, offset, model, time_period, is_retry=False):
        return self._get_request_params(offset, model, time_period, is_retry)

    def _get_data_model_1(self, type=None):
        xml_body = self._get_request_params(index=0, model=1, type=type)

        response = self.session.post(f"{self._prefix_isapi}/Traffic/ContentMgmt/dataOperation",
                                     auth=self.site.credentials,
                                     data=xml_body,
                                     timeout=self.timeout)

        if response.ok:
            self._parse_data_response_model_1(response, type)
        elif response.status_code == 503:
            self._handle_retry_request(type)

    def _handle_retry_request(self, type):
        retry_xml_body = self._get_request_params(index=self.site.camera.number, model=self.model, is_retry=True)
        response = self.session.post(
            f"{self._prefix_isapi}/Traffic/ContentMgmt/dataOperation",
            auth=self.site.credentials,
            data=retry_xml_body,
            timeout=self.timeout
        )
        if response.ok:
            self._parse_data_response_model_1(response, type)

    def _parse_data_response_model_1(self, response, type=None):
        try:
            data = parse_text_to_dict(xmltodict.parse(response.text))
            data = data["TrafficSearchResult"]

            if int(data["totalMatches"]) > 0:
                if 'matchList' in data and isinstance(data['matchList'].get('matchElement'), list) and len(
                        data["matchList"]['matchElement']) > 0:
                    self._get_url_picture(data["searchID"], data["matchList"]['matchElement'][0]["trafficData"])

                plates_type_arr =[]
                for capture in data:
                    plates_type_arr.append(self.type_of_plate(capture["trafficData"]["plate"]))

            total_matches = data["totalMatches"]
            if type == "24_hours":
                self.captures["num_captures_per_day"] = total_matches
            else:
                self.captures["num_captures"] = total_matches
        except Exception as e:
            handle_exception(e, self, "parse date response model 1")

    #TODO move to utils
    def type_of_plate(self, plate):
        type_of_plate = "UNKNOWN"
        if (plate.isdigit()):
            if (plate.length() == 8):
                return "israel"
            elif (plate.length() < 7):
                return "palestinian"
            return "israel/palestinian"
        else:
            if ("צ" in plate):
                return "idf"
            elif ("מ" in plate):
                return "israel police"
            else:
               #return palestininan_plate_check(plate)
                pass

    def palestininan_plate_check(self, plate):
        x=1



    def _parse_data_response_model_2(self, response):
        data = parse_text_to_dict(xmltodict.parse(response.text))
        data = data["CMSearchResult"]
        return data["numOfMatches"], data["responseStatusStrg"]
        # TODO: Do while til

    def _get_data_model_2(self, type=None):
        self.error_message = "מודל זה בטיפול"
        # total_matches = 0
        # xml_body = self._get_request_params(index=0, model=2)
        # response = self.session.post(f"{self._prefix_isapi}/ContentMgmt/search", auth=self.site.credentials,
        #                              data=xml_body,
        #                              timeout=self.timeout)
        #
        # if response.ok:
        #     num_matches, flag = self._parse_data_response_model_2(response)
        #     total_matches += int(num_matches)
        #     while flag == "MORE":
        #         xml_body = self._get_request_params(index=total_matches, model=2)
        #         response = self.session.post(f"{self._prefix_isapi}/ContentMgmt/search",
        #                                      auth=self.site.credentials,
        #                                      data=xml_body,
        #                                      timeout=self.timeout)
        #         if response.ok:
        #             num_matches, flag = self._parse_data_response_model_2(response)
        #             total_matches += int(num_matches)
        #             print(total_matches)
        #     x=1

    def _get_data_model_3(self, type=None):
        print("model 3 get captures")
        self.error_message = "מודל זה בטיפול"
        xml_body = self._get_request_params(index=0, model=4)
        response = self.session.post(f"{self._prefix_psia}/Custom/SelfExt/ContentMgmt/Traffic/Search",
                                     auth=self.site.credentials,
                                     data=xml_body,
                                     timeout=self.timeout)
        if response.ok:
            x = 1

    def _get_request_params(self, index, model, type=None, is_retry=False):
        start_time, end_time = get_captures_times(type)
        data_request_xml = get_body_by_model(
            model=model,
            index=index,
            start_time=start_time,
            end_time=end_time,
            camera_number=self.site.camera.number,
            is_retry=is_retry
        )
        return data_request_xml

    def ftp_status(self):
        try:
            self.ftp_1_status = self._get_ftp_status(3)
            self.ftp_2_status = self._get_ftp_status(4)
        except Exception as e:
            # handle_exception(e, self, "ftp")
            pass

    def _parse_ftp_status(self, r):
        root = ET.fromstring(r.content)

        fields = ["UploadHostEnable", "UploadHostNetStatus"]
        extracted_data = {field: root.find(field).text for field in fields if root.find(field) is not None}
        if extracted_data["UploadHostEnable"] == "0":
            extracted_data["UploadHostEnable"] = "Disable"
        else:
            extracted_data["UploadHostEnable"] = "Enable"
        if extracted_data["UploadHostNetStatus"] == "1":
            extracted_data["UploadHostNetStatus"] = 'Normal'

        return ",".join([f"{key}: {value}" for key, value in extracted_data.items()])

    def _get_ftp_status(self, index):
        r = self.session.get(
            f'{self._prefix_isapi}/Traffic/ContentMgmt/uploadModuleStatus/{index}',
            auth=self.site.credentials,
            timeout=self.timeout
        )

        if r.status_code == 200:
            extracted_data = self._parse_ftp_status(r)
        else:
            extracted_data = f"could not get ftp: {r.status}"
        return extracted_data

    def _has_playback(self, response):
        self.captures["playback"] = "V" if "<playbackURI>" in response else 'X'

    def _payload_playback(self):
        if self.playback_channel is not None:
            channel = self.playback_channel
        else:
            channel = self.site.camera.number
            print(f"playback channel doesnt configured to: {self.site}")
        start_time, end_time = get_captures_times()

        return f"""<?xml version="1.0" encoding="utf-8"?>
        <CMSearchDescription>
            <searchID>CB1EC75A-7630-0001-C44A-123015E7154D</searchID>
            <trackList>
                <trackID>{channel}01</trackID>
            </trackList>
            <timeSpanList>
                <timeSpan>
                    <startTime>{start_time}</startTime>
                    <endTime>{end_time}</endTime>
                </timeSpan>
            </timeSpanList>
            <maxResults>100</maxResults>
            <searchResultPostion>0</searchResultPostion>
            <metadataList>
                <metadataDescriptor>//recordType.meta.std-cgi.com</metadataDescriptor>
            </metadataList>
        </CMSearchDescription>
        """

    def check_amount_cameras_playback(self):
        try:
            response = self.session.get(
                f"{self._prefix_isapi}/ContentMgmt/InputProxy/channels/status",
                auth=self.site.credentials,
                timeout=self.timeout
            )

            if response.status_code != 200:
                return self._fallback_camera_list()

            xml_data = response.text.strip().split("?>")[-1].strip()
            return self._extract_ids_from_text(xml_data)

        except Exception as e:
            return [] if isinstance(e, ET.ParseError) else handle_exception(e, self, "playback")

    def _extract_ids_from_text(self, xml_text: str) -> list[int]:
        pattern = r"<id>(\d+)</id>"
        return [int(match) for match in re.findall(pattern, xml_text)]

    def _fallback_camera_list(self):
        response = self.session.get(
            f"{self._prefix_psia}/Custom/SelfExt/ContentMgmt/DynVideo/inputs/channels",
            auth=self.site.credentials,
            timeout=self.timeout
        )

        if response.status_code != 200:
            return []

        parsed_data = xmltodict.parse(response.text)
        cameras = parsed_data.get("DynVideoInputChannelList", {}).get("DynVideoInputChannel", [])
        return cameras if isinstance(cameras, list) else [cameras]

    def _get_url_picture(self, search_id, capture):
        payload = f'''
                        <PicRecInfoSearchDescription>
                            <searchID>{search_id}</searchID>
                            <VehicleList>
                                <Vehicle>
                                    <vehicleID>CA4009CB-7B60-0001-19F1-8450455078B0</vehicleID>
                                    <channel>{self.site.camera.number}</channel>
                                    <ctrl>{capture['ctrl']}</ctrl>
                                    <drive>{capture['drive']}</drive>
                                    <part>{capture['part']}</part>
                                    <fileNo>{capture['fileNo']}</fileNo>
                                    <startOffset>{capture['startOffset']}</startOffset>
                                    <picLen>{capture['picLen']}</picLen>
                                    <captureTime>{capture['captureTime']}</captureTime>
                                    <violationType>{capture['violationType']}</violationType>
                                </Vehicle>
                            </VehicleList>
                        </PicRecInfoSearchDescription>'''
        r = self.session.post(f"{self._prefix_isapi}/Traffic/ContentMgmt/picRecInfo",
                              data=payload, auth=self.site.credentials, timeout=self.timeout)
        if r.status_code == 200:
            self._parse_filename(r.text)

    def _parse_filename(self, response):
        try:
            root = ET.fromstring(response)
            ns = {'ns': root.tag.split('}')[0].strip('{')} if '}' in root.tag else {}
            for picture in root.findall('.//ns:picture', ns) if ns else root.findall('.//picture'):
                file_name = picture.find('ns:fileName', ns) if ns else picture.find('fileName')
                if file_name is not None:
                    self.example_picture = f"{self._prefix_isapi}/Traffic/ContentMgmt/Picture/{file_name.text}"
                    return
        except ET.ParseError:
            pass
