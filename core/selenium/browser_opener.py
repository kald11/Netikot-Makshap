import shutil
import sys
import os
import tempfile

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait

from core.google_sheets import GoogleSheets
from selenium.webdriver.support import expected_conditions as EC


def init_driver(url):
    options = Options()
    options.add_argument("--start-maximized")

    # Create unique Chrome user profile dir
    user_data_dir = os.path.join(tempfile.gettempdir(), next(tempfile._get_candidate_names()))
    if os.path.exists(user_data_dir):
        shutil.rmtree(user_data_dir, ignore_errors=True)
    os.makedirs(user_data_dir, exist_ok=True)
    options.add_argument(f"--user-data-dir={user_data_dir}")

    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--disable-extensions")
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)

    # Use bundled path (for PyInstaller compatibility)
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    driver_path = os.path.join(base_path, 'config', 'chromedriver.exe')

    print("Driver path:", driver_path)
    print("User data dir:", user_data_dir)

    service = Service(executable_path=driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)
    return driver


def open_site(row_number, type="nvr"):
    if not row_number.isdigit():
        return

    site, company_name = get_site(row_number)
    url = get_url(site, type)
    password = site.nvr.password if type == "nvr" else site.camera.password
    driver = init_driver(url)
    driver.implicitly_wait(8)
    enter_credentials(driver, password)


def get_site(row_number):
    gs = GoogleSheets()
    site = gs.get_row(row_number)
    return site.site, site.company_name


def get_url(site, type):
    ip = site.ip
    port = site.nvr.port if type == "nvr" else site.camera.port
    return f"http://{ip}:{port}"


def enter_credentials(driver, password):
    field_strategies = [
        ("id", "username", "password"),
        ("id", "login_user", "login_psw"),
        ("id", "loginUsername-inputEl", "loginPassword-inputEl"),
        ("css", 'input.el-input__inner[placeholder="User Name"]', 'input.el-input__inner[placeholder="Password"]')
    ]

    login_selectors = [
        (By.CSS_SELECTOR, "button.login-btn"),
        (By.ID, "b_login"),
        (By.CSS_SELECTOR, "a[title='Login']"),
        (By.ID, "loginButton")
    ]

    for by_type, user_selector, pass_selector in field_strategies:
        by = By.ID if by_type == "id" else By.CSS_SELECTOR

        if element_exists(driver, by, user_selector) and element_exists(driver, by, pass_selector):
            driver.find_element(by, user_selector).send_keys("admin")
            driver.find_element(by, pass_selector).send_keys(password)

            if user_selector == "login_user":
                buttons = driver.find_elements(By.CSS_SELECTOR, "a[btn-for='onLogin']")
                if buttons:
                    buttons[0].click()
                    return

            for by_button, value in login_selectors:
                buttons = driver.find_elements(by_button, value)
                if buttons:
                    buttons[0].click()
                    return
            break


def element_exists(driver, by, value, timeout=1):
    try:
        WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))
        return True
    except:
        return False
