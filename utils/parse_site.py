import site

from core.classes.site_class_test import SiteTest
from core.classes.Site import Site
from core.classes.company.Dahua import Dahua
from core.classes.company.Hikvision import Hikvision
from core.classes.networkComponents.Camera import Camera
from core.classes.networkComponents.Modem import Modem
from core.classes.networkComponents.Nvr import Nvr

from config.settings import Config
config = Config().get_config()


def get_results_array(cameras_array):
    results_array = []
    for camera in cameras_array:
        model = ""
        if camera.company_name == "Hikvision" and camera.device_info and isinstance(camera.device_info,
                                                                                    (list, tuple)) and len(
            camera.device_info) > 0:
            model = camera.device_info[0]
        results_array.append([camera.site.brigade, camera.site.site_name, camera.site.ip, camera.site.camera.number,
                              camera.site.camera_id, camera.company_name,
                              "V" if camera.flags["is_camera_ping"] else "X",
                              "V" if camera.flags["is_nvr_ping"] else "X",
                              overall_ping(camera.flags["is_nvr_ping"], camera.flags["is_camera_ping"]),
                              camera.captures["num_captures"],
                              camera.captures["playback"],
                              camera.error_message,
                              camera.unknowns["morning"],
                              camera.unknowns['night'],
                              camera.times["current_camera_time"],
                              camera.times["current_nvr_time"],
                              camera.times["check_time"], camera.times["is_camera_synchronized"],
                              camera.times["is_nvr_synchronized"],
                              model,
                              proper(camera.flags["is_nvr_ping"], camera.flags["is_camera_ping"],
                                     camera.captures["num_captures"], camera.site.camera_type),
                              problem(camera.flags["is_nvr_ping"], camera.flags["is_camera_ping"],
                                      camera.captures["num_captures"], camera.site.camera_type),
                              camera.ftp_1_status, camera.ftp_2_status, camera.example_picture,
                              camera.site.modem.status_code,
                              camera.site.longitude, camera.site.latitude])
    return results_array


def get_daily_results(cameras_array):
    results_array = []
    for camera in cameras_array:
        results_array.append([camera.site.brigade, camera.site.site_name, camera.site.ip, camera.site.camera.number,
                              camera.site.camera_id, camera.company_name, camera.captures["num_captures_per_day"],
                              camera.site.longitude, camera.site.latitude,
                              _status_camera_daily(camera)])
    return results_array


def _status_camera_daily(item):
    if item.site.camera_id == "אווירה":
        if not item.flags["is_nvr_ping"] or not item.flags["is_camera_ping"]:
            return "X"
        return "V"
    else:
        if item.captures["num_captures_per_day"] == "" or item.captures["num_captures_per_day"] == "0":
            return "X"
        return "V"


def problem(nvr_ping, cam_ping, captures, cam_type):
    issues = []

    if not nvr_ping:
        issues.append("NVR לא תקין")

    if not cam_ping:
        issues.append("מצלמה לא תקינה")

    # Check captures only if the camera type is "רגיל"
    if cam_type == "רגיל" and not captures:
        issues.append("אין הרכשות")

    return ", ".join(issues) if issues else "V"


def proper(nvr_ping, came_ping, captures, cam_type):
    if not nvr_ping:
        return "לא תקין"
    elif any(item in cam_type for item in ["נתיקות - אווירה", "נתיקות -טרמי", "PTZ טרמי - נתיקות", "נתיקות - PTZ"]):
        if came_ping:
            return "תקין"
        else:
            return "תקין חלקית"
    elif came_ping and captures:
        return "תקין"
    return "תקין חלקית"


def overall_ping(nvr, camera):
    if nvr and camera:
        return "V"
    elif nvr:
        return "מצלמה למטה"
    elif camera:
        return "רכיב nvr למטה"
    else:
        return "אתר למטה"


def convert_to_sites_array(df):
    data = []
    for index, row in df.iterrows():
        camera, nvr, modem = _init_classes(row)
        site = Site(row["Site Name"], row["IP Address"], camera, nvr, modem, row["Brigade"], row["Camera Id"],
                    row["Camera Type"], row["HTTPS"], row["Length"], row["Latitude"])
        item = _check_company(row, site, index)
        if item is not None:
            data.append(item)
    return data

def convert_to_sites_array_test(df):
    sites = []
    for _, row in df.iterrows():
        site = SiteTest(
            row["Check Time"],
            row["Nvr Time"],
            row["Camera Time"],
            row["Unknowns Night (22-23)"],
            row["Unknowns Morning (10-11)"],
            row["Error Reason"],
            row["Playback"],
            row["Number Captures (4 hours)"],
            row["Overall Ping"],
            row["Ping NVR"],
            row["Ping Camera"],
            row["Company"],
            row["Camera Id"],
            row["Camera Number"],
            row["IP Address"],
            row["Site Name"],
            row["Brigade"],
            row["Latitude"],
            row["Longitude"],
            row["modem status"],
            row["Example Picture"],
            row["ftp2"],
            row["ftp1"],
            row["problems"],
            row["proper"],
            row["Model NVR"],
            row["Nvr Time is synchronized"]
        )
        sites.append(site.to_dict())
    return sites


def _init_classes(row):
    camera = Camera(port=row["Camera Port"], password=row["Camera Password"], number=row["Camera Number"])
    nvr = Nvr(password=row["NVR Password"], port=row["NVR Port"])
    modem = Modem(port=row["Modem Port"], password=row["Modem Password"])
    return camera, nvr, modem


def _check_company(row, site, index):
    if "Unknowns Morning (10-11)" not in row or "Unknowns Night (22-23)" not in row:
        night = ""
        morning = ""
    else:
        morning = row["Unknowns Morning (10-11)"]
        night = row["Unknowns Night (22-23)"]
    company = row["Company"].lower().strip()
    if company == "dahua":
        return Dahua(site, index, morning, night)
    if company == "hikvision":
        return Hikvision(site, index, morning, night)
    print(
        f"Unknown company: {row['Company']}, for site: {row['Site Name']} (Ip: {row['IP Address']}) NUMBER: {row['Camera Number']}")
    return None
