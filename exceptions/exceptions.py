from config.settings import Config
from exceptions.logger import Logger

# logger = Logger.get_instance()


class ConnectionErrorException(Exception):
    """Raised when there is a connection error (e.g., RemoteDisconnected or ConnectionResetError)."""

    def __init__(self, site):
        self.message = f"The server has closed the connection. Site: {site}"
        super().__init__(self.message)


class TimeoutErrorException(Exception):
    """Raised when a timeout occurs (e.g., ConnectTimeoutError)."""

    def __init__(self, site):
        self.timeout = Config().get_config()["project_setup"]["times"]["timeout_ping"]
        self.message = f"The connection timed out ({self.timeout} seconds). Site: {site} "
        super().__init__(self.message)


class ReadTimeoutErrorException(Exception):
    """Raised when the server takes too long to respond (e.g., ReadTimeoutError)."""

    def __init__(self, site):
        self.message = f"The server takes too long to respond. Site: {site} "
        super().__init__(self.message)


class WrongProtocolError(Exception):
    """Raised when the server does not support the expected protocol (e.g., HTTP vs HTTPS)."""

    def __init__(self, site):
        self.message = f"Need to switch from http to https . Site: {site} "
        super().__init__(self.message)


def handle_exception(e, device, category="",type= "nvr"):
    ip = device.site.ip
    port = device.site.nvr.port
    error = str(e)
    site = device.site

    if any(err in error for err in ["RemoteDisconnected", "ConnectionResetError", "NewConnectionError"]):
        error = ConnectionErrorException(site)
        if len(device.error_message) == 0:
            device.error_message = "האתר למטה"
    elif "ConnectionRefusedError" in error:
        WrongProtocolError(site)
        if len(device.error_message) == 0:
            device.error_message = "לשנות לhttps"
    elif "ConnectTimeoutError" in error:
        error = TimeoutErrorException(site)
        if len(device.error_message) == 0:
            device.error_message = "החיבור לשרת נכשל עקב חריגת זמן המתנה"
    elif any(err in error for err in ["ReadTimeoutError", "HTTPConnectionPool"]):
        error = ReadTimeoutErrorException(site)
        if len(device.error_message) == 0:
            device.error_message = "לשרת לוקח יותר מדי זמן להגיב"
    elif "Wrong password" in error:

        device.error_message = f"פרטי התחברות שגויים {type}"
    elif "'Response' object has no attribute 'status'" in error:
        device.error_message = "no ftp config"
    else:
        print(f"[{category}] 'Unexpected error for {ip}:{port}")
        # logger.log("unexpected", f"Index: {device.index}.In {category} level: {error}")
        print(f"[{category}] {device.index} {error}")
        return
    print(f"[{category}] {device.index} {error}")
    # logger.log(category, f"Index: {device.index}. {error}")
