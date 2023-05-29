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
    opts.add_argument("--start-fullscreen")

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


def new_tab(driver):
    driver.switch_to.new_window("tab")
    return


def switch_to_window_number(driver, number):
    driver.switch_to.window(driver.window_handles[number - 1])
    return


def close_window_number(driver, number):
    switch_to_window_number(driver, number)
    driver.close()
    switch_to_window_number(driver, 1)
    return


def main():
    end_process = False
    while not end_process:
        server = Server("binaries/browsermob-proxy-2.1.4/bin/browsermob-proxy")
        server.start()
        proxy = server.create_proxy()

        options, caps = driver_settings(proxy.proxy, False)

        driver = webdriver.Chrome(
            service=Service("binaries/chromedriver"),
            options=options,
            desired_capabilities=caps,
        )

        proxy.new_har("google")

        driver.get("https://lms.partaonline.ru/")

        time.sleep(10)

        try:
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

            urls_json = json.load(open("downloads/urls.json"))

            mpd_urls_json = dict()

            for url in urls_json["urls"]:
                new_tab(driver)
                close_window_number(driver, 1)

                driver.get(url)

                time.sleep(15)

                title_div = driver.find_element(
                    By.CLASS_NAME, "page-description__info__description"
                )
                title_text = title_div.find_element(By.TAG_NAME, "h1").text

                if "Обществознание" in title_text:
                    mpd_urls = []
                    videos = driver.find_elements(By.CLASS_NAME, "content__video")

                    for i, video in enumerate(videos):
                        if i == len(videos) - 1 and not len(videos) == 1:
                            driver.execute_script(
                                "window.scrollTo(0, document.body.scrollHeight);"
                            )
                        else:
                            video.location_once_scrolled_into_view

                        time.sleep(3)
                        video.click()
                        time.sleep(10)
                        video.click()
                        time.sleep(3)

                    har_logs = proxy.har  # type is dict
                    for entry in har_logs["log"]["entries"]:
                        if entry["request"]["url"].endswith(".mpd"):
                            mpd_urls.append(entry["request"]["url"])

                    mpd_urls_json[title_text] = mpd_urls

                    print(mpd_urls)

            with open("downloads/mpd_urls.json", "w") as outfile:
                outfile.write(json.dumps(mpd_urls_json, ensure_ascii=False))
            outfile.close()

            end_process = True
        except Exception as error:
            print(error)
            end_process = True
            # driver.close()

    # time.sleep(1000)
    driver.close()


if __name__ == "__main__":
    main()
