import pandas as pd
from core.classes.Site import Site
from core.classes.company.Dahua import Dahua
from core.classes.company.Hikvision import Hikvision
from core.classes.networkComponents.Camera import Camera
from core.classes.networkComponents.Nvr import Nvr
from core.classes.networkComponents.Modem import Modem
import threading


# ----------------------- Arrays and df functions -----------------------
def columns_to_rows_array(columns):
    return [list(row) for row in zip(*columns)]


def array_to_df(data):
    return pd.DataFrame(data[1:], columns=data[0])


def convert_to_sites_array(df):
    data = []
    for index, row in df.iterrows():
        camera, nvr, modem = _init_classes(row)
        site = Site(row["Site Name"], row["IP Address"], camera, nvr, modem)
        item = _check_company(row, site)
        if item is not None:
            data.append(item)
    return data


# ----------------------- Threads functions -----------------------
def use_thread(cameras_array, worker):
    threads = []

    for camera in cameras_array:
        thread = threading.Thread(target=worker, args=(camera,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()


# ----------------------- Private Functions -----------------------

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
