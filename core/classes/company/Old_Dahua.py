class DahuaDevice(NVRDevice):
    def __init__(self, ip, password, port=90, check_time=datetime.now(), start_time=datetime.now(), username="admin",
                 verbose=True,
                 auto_login=True):
        self.session_id = None
        self.mediaFindObjectId = None
        self.rpc_request_id = 0
        NVRDevice.__init__(self, ip, password, port=port, check_time=check_time, username=username, verbose=verbose,
                           auto_login=auto_login, start_time=start_time)

    def datetime_to_str(self, dt):
        return dt.strftime("%Y-%m-%d%%20%H:%M:%S")

    def rpc_request(self, url, method, params, add_data={}):
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

    def get_device_info(self):
        if self.flags["Login OK"] is None:
            self.flags["Login OK"] = self.try_login()

        if self.flags["Login OK"]:
            r = self.rpc_request(f"http://{self.ip}:{self.port}/RPC2", method="magicBox.getDeviceType",
                                 params="")
            if r is not None:
                self.device_info = r["params"]["type"]

        return self.device_info

    def try_login(self):
        if self.flags["Remote"]:
            url = f'http://{self.ip}:{self.port}/RPC2_Login'

            r = self.rpc_request(url, method="global.login",
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

    def tryLogout(self):
        self.rpc_request(f"http://{self.ip}:{self.port}/RPC2", method="global.logout",
                         params=None)
        self.session.close()

    def get_connected_cameras(self):
        if self.flags["Login OK"]:
            ch_count = 0
            if self.device_info in ["ITSE0804-GN5B-D"]:
                r = self.rpc_request(f"http://{self.ip}:{self.port}/RPC2", method="eventManager.getEventData",
                                     params={"code": "NetDevicesInfo", "index": 0, "name": ""})
                if r is not None and r["result"] and r["params"]["data"][0]["Devices"] is not None:
                    ch_count = len(r["params"]["data"][0]["Devices"])
            elif self.device_info in ["ITC952-AF3F-IR7"]:  # this is a single camera
                ch_count = 1
            elif self.device_info in ["DH-XVR5104HS-4KL-X-1TB"]:
                r = self.rpc_request(f"http://{self.ip}:{self.port}/RPC2", method="LogicDeviceManager.getCameraState",
                                     params={"uniqueChannels": [-1]})
                ch_count = len([c for c in r["params"]["states"] if c['connectionState'] == 'Connected'])
            else:
                print(self.device_info)

            if self.verbose:
                print(f"Found {ch_count} connected cameras for Dahua IP {self.ip}")

            self.cameras = range(1, ch_count + 1)
            return self.cameras

        self.cameras = []
        return self.cameras

    def check_nvr(self, mins=30):
        try:
            self.resetFlags()
            if self.flags["Login OK"]:
                self.flags["Clock Synced"] = self.set_datetime(datetime.now())
                if self.flags["Camera Count"] > 0:
                    self.flags.pop("All")

                    for cam in self.cameras:
                        lpr_works, lpr_results = self.checkLPR(cam)
                        self.flags[cam] = {"LPR": lpr_works, "LPR COUNT": len(lpr_results),
                                           "Playback": self.checkPlayback(cam, mins=mins),
                                           "Live": self.checkLiveView(cam)}

                    self.destroy_media_find_object()

                self.tryLogout()

            return self.flags
        except (requests.ReadTimeout, requests.exceptions.ConnectionError):
            return self.timeout_flags

    def create_media_find_object(self):
        if self.mediaFindObjectId is None:
            r = self.session.get(f"http://{self.ip}:{self.port}/cgi-bin/mediaFileFind.cgi?action=factory.create",
                                 auth=self.credentials, timeout=DEFAULT_TIMEOUT)
            if r.ok:
                self.mediaFindObjectId = r.text.split('=')[-1].strip("\x0a\x0d")
                return True
            else:
                return False
        else:
            return True

    def close_media_find_object(self):
        if self.mediaFindObjectId is not None:
            self.session.get(
                f"http://{self.ip}:{self.port}/cgi-bin/mediaFileFind.cgi?action=close&object={self.mediaFindObjectId}",
                auth=self.credentials, timeout=DEFAULT_TIMEOUT)

    def destroy_media_find_object(self):
        if self.mediaFindObjectId is not None:
            self.session.get(
                f"http://{self.ip}:{self.port}/cgi-bin/mediaFileFind.cgi?action=destroy&object={self.mediaFindObjectId}",
                auth=self.credentials, timeout=DEFAULT_TIMEOUT)

            self.mediaFindObjectId = None

    def parse_media_file_find(self, result_entry):
        entry_split = result_entry.split('\r\n')
        if not entry_split[0].startswith("found="):
            return []

        if int(entry_split[0].split('=')[-1]) == 0:
            return []

        items = {}
        for entry in entry_split[1:]:
            if entry.startswith("items["):
                entry = entry[len("items["):]
                ind = int(entry[:entry.index("]")])
                if ind not in items:
                    items[ind] = {}

                entry = entry[entry.index("]") + 2:]
                if entry.startswith("Type"):
                    items[ind]["type"] = entry[len("Type="):]
                elif entry.startswith("Summary.TrafficCar.PlateNumber"):
                    items[ind]["plate"] = entry[len("Summary.TrafficCar.PlateNumber="):]
                elif entry.startswith("StartTime"):
                    items[ind]["time"] = entry[len("StartTime="):]
                elif entry.startswith("EndTime"):
                    items[ind]["end"] = entry[len("EndTime="):]

        if len(items) == 0:
            return []

        return list(items.values())

    def getLPR(self, cam_id, last_capture_time):
        if self.create_media_find_object():
            length_captures = 0
            self.session.get(
                f"http://{self.ip}:{self.port}/cgi-bin/mediaFileFind.cgi?action=findFile&object={self.mediaFindObjectId}&condition.Channel={cam_id}&condition.StartTime={self.start_time}&condition.EndTime={self.check_time}&condition.Types[0]=jpg",
                auth=self.credentials, timeout=DEFAULT_TIMEOUT)

            r = self.session.get(
                f"http://{self.ip}:{self.port}/cgi-bin/mediaFileFind.cgi?action=findNextFile&object={self.mediaFindObjectId}&count=5000",
                # no limit
                auth=self.credentials, timeout=DEFAULT_TIMEOUT)
            items = self.parse_media_file_find(r.text)
            items = [i for i in items if len(i["plate"]) > 0 and i["plate"].lower() != "unknown"]
            length_captures += len(items)
            if length_captures == 0:
                self.close_media_find_object()
                return Capture(last_cap_time=last_capture_time, cap_amount='0', is_captured='לא')
            last_capture = items[-1]['end']
            while len(items) != 0:
                r = self.session.get(
                    f"http://{self.ip}:{self.port}/cgi-bin/mediaFileFind.cgi?action=findNextFile&object={self.mediaFindObjectId}&count=5000",
                    # no limit
                    auth=self.credentials, timeout=DEFAULT_TIMEOUT)
                items = self.parse_media_file_find(r.text)
                # items = [i for i in items if len(i["plate"]) > 0 and i["plate"].lower() != "unknown"]
                if len(items) > 0: last_capture = items[-1]['end']
                length_captures += len(items)
            # items = [i for i in items if len(i["plate"]) > 0 and i["plate"].lower() != "unknown"]
            self.close_media_find_object()
            return Capture(last_cap_time=last_capture, cap_amount=length_captures, is_captured='כן')

        return Capture(last_cap_time=last_capture_time, cap_amount='0', is_captured='לא')

    def checkPlayback(self, cam_id, mins=30):
        if self.create_media_find_object():
            self.session.get(
                f"http://{self.ip}:{self.port}/cgi-bin/mediaFileFind.cgi?action=findFile&object={self.mediaFindObjectId}&condition.Channel={cam_id}&condition.StartTime={self.datetime_to_str(self.check_time - td(minutes=mins + 1))}&condition.EndTime={self.datetime_to_str(self.check_time)}&condition.Types[0]=dav0&condition.Types[1]=mp4",
                auth=self.credentials, timeout=DEFAULT_TIMEOUT)

            r = self.session.get(
                f"http://{self.ip}:{self.port}/cgi-bin/mediaFileFind.cgi?action=findNextFile&object={self.mediaFindObjectId}&count=5",
                auth=self.credentials, timeout=DEFAULT_TIMEOUT)

            items = self.parse_media_file_find(r.text)
            if len(items) > 0:
                cap_at_start, cap_at_end = items[0]["time"], items[0]["end"]

                if self.verbose:
                    print(
                        f"Found Playback video from Dahua IP {self.ip}. From camera {cam_id} start: {cap_at_start} end: {cap_at_end}")

                return True

        return False

    def tryLiveView(self, cam_id, stream_type=1, max_retries=None, max_frames_count=-1):
        if not ping(self.ip, 554, timeout_secs=10):
            return False

        stream = cv2.VideoCapture(
            f'rtsp://{self.username}:{self.password}@{self.ip}:554/cam/realmonitor?channel={cam_id}&subtype={stream_type}')
        return self.baseLiveView(stream, cam_id, max_retries=max_retries, max_frames_count=max_frames_count)

    def set_datetime(self, new_datetime):
        if self.flags["Login OK"]:
            r = self.session.get(
                f"http://{self.ip}:{self.port}/cgi-bin/global.cgi?action=setCurrentTime&time={self.datetime_to_str(new_datetime)}",
                auth=self.credentials)

            return r.status_code == 200

        return False

    def get_current_datetime(self):
        if self.flags["Login OK"]:
            y = DEFAULT_DATETIME
            url = f"http://{self.ip}:{self.port}/RPC2"
            r = self.rpc_request(url=url, method='global.getCurrentTime', params=None)
            if r['result']:
                current_time = r['params']['time']
                current_time = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S')
                return current_time
        return DEFAULT_DATETIME