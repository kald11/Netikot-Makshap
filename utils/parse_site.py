from core.classes.Site import Site
from core.classes.company.Dahua import Dahua
from core.classes.company.Hikvision import Hikvision
from core.classes.networkComponents.Camera import Camera
from core.classes.networkComponents.Modem import Modem
from core.classes.networkComponents.Nvr import Nvr


def get_results_array(cameras_array):
    results_array = []
    for camera in cameras_array:
        results_array.append([camera.site.brigade, camera.site.site_name, camera.site.ip, camera.site.camera.number,
                              camera.site.camera_id, camera.company_name, "V" if camera.flags["is_cam_ping"] else "X",
                              "V" if camera.flags["is_nvr_ping"] else "X", camera.captures["num_captures"],
                              camera.error_message,
                              camera.unknown_morning,
                              camera.unknown_night,
                              camera.times["current_camera_time"],
                              camera.times["check_time"], camera.times["is_synchronized"]])
    return results_array


def convert_to_sites_array(df):
    data = []
    for index, row in df.iterrows():
        camera, nvr, modem = _init_classes(row)
        site = Site(row["Site Name"], row["IP Address"], camera, nvr, modem, row["Brigade"], row["Camera Id"])
        item = _check_company(row, site)
        if item is not None:
            data.append(item)
    return data


def _init_classes(row):
    camera = Camera(port=row["Camera Port"], password=row["Camera Password"], number=row["Camera Number"])
    nvr = Nvr(password=row["NVR Password"], port=row["NVR Port"])
    modem = Modem(port=row["Modem Port"], password=row["Modem Password"])
    return camera, nvr, modem


def _check_company(row, site):
    if row["Company"] == "Dahua":
        item = Dahua(site)
    elif row["Company"] == "Hikvision":
        item = Hikvision(site)
    else:
        print(f"Unknown company: {row['Company']}, for site: {row['site_name']} (ID: {row['id']})")
        item = None
    return item
