class camera;
    def __init__(self, site_name, IP_address, camera_port, camera_password, nvr_port, nvr_password, camera_id,
                 wifi_name, wifi_password):
        self.site_name = site_name
        self.IP_address = IP_address
        self.camera_port = camera_port
        self.camera_password = camera_password
        self.nvr_port = nvr_port
        self.nvr_password = nvr_password
        self.camera_id = camera_id
        self.wifi_name = wifi_name
        self.wifi_password = wifi_password

    # method to get camera information in a dictionary format for easy access and display
    def get_info(self):
        return {
            "Site Name": self.site_name,
            "IP Address": self.IP_address,
            "Camera Port": self.camera_port,
            "Camera Password": self.camera_password,
            "NVR Port": self.nvr_port,
            "NVR Password": self.nvr_password,
            "Camera ID": self.camera_id,
            "WiFi Name": self.wifi_name,
            "WiFi Password": self.wifi_password
        }

    # methods to get specific camera information
    def get_site_name_info(self):
        return self.site_name

    def get_ip_address_info(self):
        return self.IP_address

    def get_camera_port_info(self):
        return self.camera_port

    def get_camera_password_info(self):
        return self.camera_password

    def get_nvr_port_info(self):
        return self.nvr_port

    def get_nvr_password_info(self):
        return self.nvr_password

    def get_camera_id_info(self):
        return self.camera_id

    def get_wifi_name_info(self):
        return self.wifi_name

    def get_wifi_password_info(self):
        return self.wifi_password


