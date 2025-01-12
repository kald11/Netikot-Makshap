from core.classes.Site import Site
from core.classes.company.Hikvision import Hikvision
from core.classes.networkComponents.Camera import Camera

site = Site(site_name="",ip="",camera=Camera(port="2081", password="", number=""),nvr=Nvr(),modem=Modem(),brigade="",camera_id="")
hik = Hikvision()