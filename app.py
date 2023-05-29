from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.service import Service

from browsermobproxy import Server

import time
import json
import os


def driver_settings(proxy, headless: bool = True):
    opts = Options()

    caps = DesiredCapabilities.CHROME
    caps["goog:loggingPrefs"] = {"performance": "ALL"}

    if headless:
        opts.add_argument("--headless")

    opts.add_argument("--ignore-certificate-errors")
    opts.add_argument("--proxy-server={0}".format(proxy))

    return opts, caps


def process_browser_log_entry(entry):
    response = json.loads(entry["message"])["message"]
    return response


def process_browser_logs_for_network_events(logs):
    """
    Return only logs which have a method that start with "Network.response", "Network.request", or "Network.webSocket"
    since we're interested in the network events specifically.
    """
    for entry in logs:
        log = json.loads(entry["message"])["message"]
        if (
            "Network.response" in log["method"]
            or "Network.request" in log["method"]
            or "Network.webSocket" in log["method"]
        ):
            yield log


def main():
    try:
        server = Server("binaries/browsermob-proxy-2.1.4/bin/browsermob-proxy")
        server.start()
        proxy = server.create_proxy()

        options, caps = driver_settings(proxy.proxy, False)
        url = "https://lms.partaonline.ru/"

        driver = webdriver.Chrome(
            service=Service("binaries/chromedriver"),
            options=options,
            desired_capabilities=caps,
        )

        proxy.new_har("google")

        driver.get(url)

        # try:
        #     advanced_button = driver.get(By.ID, "details-button")
        #     advanced_button.click()

        #     time.sleep(3)

        #     proceed_button = driver.get(By.ID, "proceed-link")
        #     proceed_button.click()

        # except Exception as error:
        #     print(error)

        time.sleep(10)

        signin_button = driver.find_element(By.CLASS_NAME, "button")
        signin_button.click()

        time.sleep(5)

        inputs = driver.find_elements(By.CLASS_NAME, "oauth_form_input")
        phone_input = inputs[0]
        phone_input.send_keys("+79065472854")
        password_input = inputs[1]
        password_input.send_keys("@interval8#")

        time.sleep(5)

        vk_signin_button = driver.find_element(By.CLASS_NAME, "flat_button")
        vk_signin_button.click()

        time.sleep(5)

        moi_gruppy = driver.find_element(By.CLASS_NAME, "group__item")
        moi_gruppy.click()

        time.sleep(5)

        lessons = driver.find_elements(By.CLASS_NAME, "list__item")
        lesson_button = lessons[0].find_element(By.CLASS_NAME, "link")
        lesson_button.click()

        time.sleep(10)

        video = driver.find_element(By.CLASS_NAME, "content__video")
        video.click()

        time.sleep(10)

        har_logs = proxy.har  # type is dict
        url = ""
        for entry in har_logs["log"]["entries"]:
            if entry["request"]["url"].endswith(".mpd"):
                url = entry["request"]["url"]
        print(url)

    except Exception as error:
        print(error)

    time.sleep(1000)
    driver.close()


if __name__ == "__main__":
    main()
