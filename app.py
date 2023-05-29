from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import json
import pprint


def driver_settings(headless: bool = True):
    opts = Options()
    caps = DesiredCapabilities.CHROME
    caps["goog:loggingPrefs"] = {"performance": "ALL"}
    if headless:
        opts.add_argument(" --headless")
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
    options, caps = driver_settings(False)
    driver = webdriver.Chrome(
        "chromedriver", options=options, desired_capabilities=caps
    )
    url = "https://lms.partaonline.ru/"
    driver.get(url)

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

    logs = driver.get_log("performance")

    with open("logs.json", "w", encoding="utf-8") as f:
        f.write("[")

        # Iterates every logs and parses it using JSON
        for log in logs:
            network_log = json.loads(log["message"])["message"]

            if (
                "Network.response" in network_log["method"]
                or "Network.request" in network_log["method"]
            ):
                f.write(json.dumps(network_log) + ",")
                params = network_log.get("params", {})
                response = params.get("response", {})
                url: str = response.get("url", None)
                if url is not None:
                    print(url)

        f.write("{}]")

    # while True:
    #     browser_log = driver.get_log("performance")
    #     events = [process_browser_log_entry(entry) for entry in browser_log]
    #     events = [event for event in events if "Network.response" in event["method"]]
    #     if len(events) > 0:
    #         with open("logs.json", "a") as write_file:
    #             write_file.write(str(events))
    #             write_file.write("\n")
    #         write_file.close()
    #     for e in events:
    #         params = e.get("params", {})
    #         response = params.get("response", {})
    #         url: str = response.get("url", None)
    #         if url is None:
    #             continue
    #         if "master" in url:
    #             print(url)
    #             break
    #     else:
    #         continue
    #     break

    time.sleep(1000)
    driver.close()


if __name__ == "__main__":
    main()
