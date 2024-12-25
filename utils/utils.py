import pandas as pd
from core.classes.Site import Site
from core.classes.Dahua import Dahua
from core.classes.Hikvision import Hikvision
from core.classes.Camera import Camera
from core.classes.Nvr import Nvr
from core.classes.Modem import Modem


# ----------------------- Arrays and df functions -----------------------
def columns_to_rows_array(columns):
    return [list(row) for row in zip(*columns)]


def array_to_df(data):
    return pd.DataFrame(data[1:], columns=data[0])


def convert_to_sites_array(df):
    data = []
    for index, row in df.iterrows():
        camera, nvr, modem = _init_classes(row)
        site = Site(row["site_name"], row["ip"], camera, nvr, modem)
        item = _check_company(row, site)
        if item is None:
            data.append(item)
    return data


# ----------------------- Private Functions -----------------------

def _init_classes(row):
    camera = Camera(row["id"], row["password"], row["number"], row["id"])
    nvr = Nvr(password=row["nvr password"], port=row["nvr_port"])
    modem = Modem(port=row["modem_port"], password=row["modem_password"])
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
