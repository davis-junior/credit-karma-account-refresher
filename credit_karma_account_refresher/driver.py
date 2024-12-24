from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver

from constants import DESKTOP_USER_AGENT, WEB_DRIVER_PORT


def get_new_driver() -> WebDriver:
    print("Getting new driver...")

    # possible arguments: https://peter.sh/experiments/chromium-command-line-switches/
    options = webdriver.ChromeOptions()
    options.add_argument(f"--user-agent={DESKTOP_USER_AGENT}")
    options.add_argument("start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--incognito")
    options.set_capability("goog:loggingPrefs", {"browser": "ALL"})
    options.add_argument("--disable-blink-features=AutomationControlled")

    # to keep browser open for testing (also comment driver.quit() at end of script)
    # options.add_experimental_option("detach", True)

    driver = webdriver.Chrome(
        options=options, service=webdriver.ChromeService(port=WEB_DRIVER_PORT)
    )
    driver.command_executor._url = f"http://localhost:{WEB_DRIVER_PORT}"

    # causes infinite page load on Credit Karma
    # issue is chrome_runtime(...) which invokes an internal JavaScript script
    # TODO: fork project and fix issue, then uncomment this block
    # stealth(
    #     driver,
    #     user_agent=DESKTOP_USER_AGENT,
    #     languages=["en-US", "en"],
    #     vendor="Google Inc.",
    #     platform="Win32",
    #     webgl_vendor="Intel Inc.",
    #     renderer="Intel Iris OpenGL Engine",
    #     fix_hairline=True,
    #     run_on_insecure_origins=True,
    # )

    print(f"Driver user agent: {driver.execute_script('return navigator.userAgent')}")
    return driver
