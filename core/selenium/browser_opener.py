from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


def open_site(url):
    options = Options()
    options.add_argument("--start-maximized")

    service = Service()  # optionally point to chromedriver
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)
