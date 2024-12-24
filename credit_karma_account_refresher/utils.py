from selenium.webdriver.chrome.webdriver import WebDriver


def does_log_contain_any_string(driver: WebDriver, search_str_list: list["str"]):
    logs = driver.execute_script("return window.logs;")
    for entry in logs:
        if type(entry) is dict:
            message = str(entry["message"])
        else:
            message = str(entry)

        for search_str in search_str_list:
            if search_str.lower() in message.lower():
                return entry
