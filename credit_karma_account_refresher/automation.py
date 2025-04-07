import sqlite3
import time
import traceback

from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from constants import PARENT_CREDENTIAL_ACCOUNT
from credentials import get_child_username, get_password
from db import add_db_record
from globals import current_otp_dict_list
from otp import get_otp, update_otp
from utils import does_log_contain_any_string


def refresh_accounts(
    driver: WebDriver, cursor: sqlite3.Cursor, parent_username: str, parent_password: str
):
    global current_otp_dict_list

    print(f"Refreshing accounts for username {parent_username}...")

    # navigate to URL
    print("Navigating to login page...")
    try:
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
    except:
        pass

    driver.maximize_window()
    time.sleep(1)

    driver.get("https://www.creditkarma.com/auth/logon")
    try:
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
    except:
        pass

    time.sleep(2)

    attempt = 0
    while attempt < 10:
        attempt += 1

        username_input_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input#username"))
        )

        password_input_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input#password"))
        )

        # login_button_element = WebDriverWait(driver, 10).until(
        #     EC.presence_of_element_located((By.CSS_SELECTOR, "button#Logon"))
        # )

        print("Logging in...")

        username_input_element.click()
        time.sleep(1)
        username_input_element.clear()
        username_input_element.send_keys(parent_username)
        time.sleep(1)
        username_input_element.send_keys(Keys.TAB)
        # password_input_element.click()
        time.sleep(2)

        password_input_element.clear()
        password_input_element.send_keys(parent_password)
        time.sleep(2)

        original_url = driver.current_url
        update_otp("credit karma", parent_username, "")

        # login_button_element.click()
        password_input_element.send_keys(Keys.ENTER)

        try:
            WebDriverWait(driver, 10).until(EC.url_changes(original_url))
        except:
            print("URL did not change. Trying again in 10 seconds...")
            time.sleep(10)
            continue

        try:
            driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
        except:
            pass

        # checking if there was an error logging in
        if "referenceerror" in driver.current_url.lower():
            print(
                "Reference error showing. Need to navigate back to login page to try again. Trying again in 10 seconds..."
            )
            time.sleep(10)
            original_url = driver.current_url
            driver.get("https://www.creditkarma.com/auth/logon")
            try:
                driver.execute_script(
                    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
                )
            except:
                pass

            time.sleep(2)
            continue
        elif "error_code" in driver.current_url.lower():
            print("Error logging in. Trying again in 10 seconds...")
            original_url = driver.current_url
            time.sleep(10)
            continue
        else:
            break

    skip_sms_mfa = False
    # I have not seen where Credit Karma skips SMS MFA even if unenrolled, but leaving code here for now
    # in case they make this possible. Shouldn't break anything by leaving it here.
    if "/today" in driver.current_url:
        print(
            "/today in current URL, so likely already logged in. Skipping SMS MFA handling..."
        )
        skip_sms_mfa = True

    if not skip_sms_mfa:
        print("Checking if page has the send SMS code button...")
        # handle other page and send code button sometimes
        try:
            send_sms_code_input_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "button[data-testid='send-code-btn']")
                )
            )

            time.sleep(2)
            original_url = driver.current_url
            print("Found send SMS code button. Clicking now to send SMS message...")
            send_sms_code_input_element.click()

            WebDriverWait(driver, 10).until(EC.url_changes(original_url))
        except:
            print("No send code page, so likely SMS code already sent")

    try:
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
    except:
        pass

    if not skip_sms_mfa:
        print("Waiting for actual SMS code input page to sign in...")
        sms_code_input_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='tel']"))
        )

        print(
            "Found SMS code input. Waiting for SMS forwarder app and Flask server to retrieve code..."
        )
        # wait for global otp to not be empty -- Flask thread should set it
        try:
            WebDriverWait(driver, 30).until(
                lambda driver: get_otp("credit karma", parent_username) != ""
            )
        except:
            traceback.print_exc()
            print("Did not get SMS code")

        if get_otp("credit karma", parent_username) == "":
            # although it's possible to skip SMS code MFA here if your accoount is not encrolled,
            # it will be required later to get to the linked accounts page
            raise Exception("Did not get SMS code")

            # # check for close button which is skip button. For some reason they show the SMS code prompt
            # # but allow you to bypass if your account secruity is unenrolled
            # print("Checking for skip button, which will work to skip MFA if account security setting is unenrolled")
            # skip_button = WebDriverWait(driver, 10).until(
            #     EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-testid='skip-button']"))
            # )
            # print("Found skip button. Clicking now...")
            # original_url = driver.current_url
            # skip_button.click()
            # time.sleep(2)

            # # wait for URL https://www.creditkarma.com/today
            # WebDriverWait(driver, 10).until(
            #     EC.url_changes(original_url)
            # )

            # skip_sms_mfa = True

    if skip_sms_mfa or get_otp("credit karma", parent_username):
        if not skip_sms_mfa:
            print(
                f"Retrieved code {get_otp('credit karma', parent_username)}. Attempting sign in with it..."
            )
            original_url = driver.current_url

            time.sleep(1)
            sms_code_input_element.send_keys(get_otp("credit karma", parent_username))
            time.sleep(1)
            sms_code_input_element.send_keys(Keys.ENTER)

            WebDriverWait(driver, 15).until(EC.url_changes(original_url))

        # wait for URL https://www.creditkarma.com/today
        WebDriverWait(driver, 30).until(EC.url_matches("/today"))

        print("Successfully signed in")
        try:
            driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
        except:
            pass

        time.sleep(2)

        accounts_attempted_list = []

        print("Navigating to linked accounts page...")
        driver.get("https://www.creditkarma.com/connect/manage-accounts")
        try:
            driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
        except:
            pass

        failed_attempt = 0
        while (
            failed_attempt < 25
        ):  # current have 22 accounts in my credit karma, so set a little higher in case all error
            failed_attempt += 1  # subtracting 1 after each successful refresh

            if not "/manage-accounts" in driver.current_url:
                print("URL is different. Navigating to linked accounts page...")
                driver.get("https://www.creditkarma.com/connect/manage-accounts")

            driver.switch_to.default_content()

            try:
                driver.execute_script(
                    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
                )
            except:
                pass

            time.sleep(2)

            if "/verify-phone/" in driver.current_url:
                # TODO: handle SMS code here also by refactoring above code and calling refactored function
                raise Exception(
                    "Found prompt for SMS code again. Cannot skip these ones though. Exiting refresh function since this is not handled yet."
                )

            try:
                # wait for at least 1 iframe
                WebDriverWait(driver, 60).until(
                    lambda driver: driver.execute_script("return frames.length") > 0
                )

                # switch to correct iframe that contains the accounts container elem below
                # note it is a nested one, so need to switch frames 2 or more times
                accounts_container_elem = None
                parent_frames_length = driver.execute_script("return frames.length")
                for i in range(parent_frames_length):
                    driver.switch_to.frame(i)

                    # likely not in parent iframe, but check in case of website redesign
                    # all accounts are in this div
                    try:
                        accounts_container_elem = WebDriverWait(driver, 20).until(
                            EC.presence_of_element_located(
                                (By.CSS_SELECTOR, ".fdx-provider-results")
                            )  # timeout error here
                        )
                    except:
                        pass

                    if accounts_container_elem is not None:
                        print(f"Found accounts container elem in parent frame {i}")
                        break

                    child_frames_length = driver.execute_script("return frames.length")
                    if child_frames_length > 0:
                        for i2 in range(child_frames_length):
                            driver.switch_to.frame(i2) # exception here sometimes, caught by surrounding try block
                            # all accounts are in this div
                            try:
                                accounts_container_elem = WebDriverWait(driver, 30).until(
                                    EC.presence_of_element_located(
                                        (By.CSS_SELECTOR, ".fdx-provider-results")
                                    )  # timeout error here
                                )
                            except:
                                pass

                            if accounts_container_elem is not None:
                                print(
                                    f"Found accounts container elem in parent frame {i}, child frame {i2}"
                                )
                                break

                    if accounts_container_elem is not None:
                        break

                if accounts_container_elem is None:
                    driver.switch_to.default_content()
                    raise Exception("Could not find accounts container in any iframe")
            except:
                traceback.print_exc()

                print("Navigating to linked accounts page...")
                driver.get("https://www.creditkarma.com/connect/manage-accounts")
                try:
                    driver.execute_script(
                        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
                    )
                except:
                    pass
                time.sleep(2)

                continue

            # inject console log to global var
            script = """
                window.logs = [];
                console.log = function(msg) { logs.push({level: "INFO", message: msg}); };
                console.info = function(msg) { logs.push({level: "INFO", message: msg}); };
                console.warn = function(msg) { logs.push({level: "WARNING", message: msg}); };
                console.error = function(msg) { logs.push({level: "SEVERE", message: msg}); };
            """
            driver.execute_script(script)

            error = False
            need_refresh = False

            # each card (account/site/business) is a direct child div of container elem
            account_elems = accounts_container_elem.find_elements(By.XPATH, "./*")
            for account_elem in account_elems:
                # account/site/business name
                account_name_elem = account_elem.find_element(
                    By.CSS_SELECTOR, "p.fdx-provider-search-result-detail-name"
                )
                account_name = account_name_elem.get_attribute("textContent").strip()

                if account_name in accounts_attempted_list:
                    continue

                accounts_attempted_list.append(account_name)

                if account_name in ["NelNet Student Loan"]:
                    print(f"Skipping account {account_name}")
                    add_db_record(
                        cursor,
                        parent_username,
                        account_name,
                        "SKIPPED",
                        "Manually specified to skip",
                    )
                    continue

                refresh_alread_initiated_and_console_cleared = False

                # handle accounts that need reconnected
                try:
                    error_notification_elem = None
                    error_notification_elem = account_elem.find_element(By.CSS_SELECTOR, "p.fdx-mc-error-notification-message")
                    if "our connection to this account expired" in error_notification_elem.text.lower():
                        print("Connection expired text detected and need to reconnect account")
                        
                        reconnect_button1 = account_elem.find_element(By.CSS_SELECTOR, "button.fdx-mc-error-notification-action")
                        actions = ActionChains(driver)
                        actions.scroll_to_element(reconnect_button1)
                        actions.perform()
                        reconnect_button1.click()
                        time.sleep(2)

                        # DOM reloads here, so wait for next reconnect button
                        reconnect_button2 = WebDriverWait(driver, 15).until(
                            EC.presence_of_element_located(
                                (By.CSS_SELECTOR, "button[aria-label='Reconnect']")
                            )
                        )
                        actions = ActionChains(driver)
                        actions.scroll_to_element(reconnect_button2)
                        actions.perform()

                        reconnect_button2.click()
                        time.sleep(2)

                        # a new window will open where you directly sign in here
                        original_window_handle = driver.current_window_handle
                        WebDriverWait(driver, 15).until(EC.number_of_windows_to_be(2))
                        switched_windows = False

                        try:
                            for window_handle in driver.window_handles:
                                if window_handle != original_window_handle:
                                    driver.switch_to.window(window_handle)
                                    switched_windows = True
                                    print("Switched to new window")

                                    if "americanexpress.com" in driver.current_url:
                                        child_account = "American Express"
                                    elif "citi.com" in driver.current_url:
                                        child_account = "Citi"
                                    else:
                                        raise Exception(f"Unsupported site to sign in with credentials: {driver.current_url}")
                                    
                                    child_username = get_child_username(PARENT_CREDENTIAL_ACCOUNT, parent_username, child_account)
                                    child_password = get_password(PARENT_CREDENTIAL_ACCOUNT, parent_username, child_account, child_username)

                                    if not child_username or not child_password:
                                        raise Exception(f"No credentials found for child account {child_account} under parent user {parent_username}")

                                    if "americanexpress.com" in driver.current_url:
                                        user_id_input_elem = WebDriverWait(driver, 15).until(
                                            EC.presence_of_element_located(
                                                (By.CSS_SELECTOR, "input#eliloUserID")
                                            )
                                        )

                                        password_input_elem = WebDriverWait(driver, 15).until(
                                            EC.presence_of_element_located(
                                                (By.CSS_SELECTOR, "input#eliloPassword")
                                            )
                                        )
                                    elif "citi.com" in driver.current_url:
                                        user_id_input_elem = WebDriverWait(driver, 15).until(
                                            EC.presence_of_element_located(
                                                (By.CSS_SELECTOR, "input#userid_input_mask")
                                            )
                                        )

                                        password_input_elem = WebDriverWait(driver, 15).until(
                                            EC.presence_of_element_located(
                                                (By.CSS_SELECTOR, "input#password_input")
                                            )
                                        )

                                    print(f"Logging in to {child_account}...")

                                    user_id_input_elem.click()
                                    time.sleep(1)
                                    user_id_input_elem.clear()
                                    user_id_input_elem.send_keys(child_username)
                                    time.sleep(1)
                                    user_id_input_elem.send_keys(Keys.TAB)
                                    # password_input_elem.click()
                                    time.sleep(2)

                                    password_input_elem.clear()
                                    password_input_elem.send_keys(child_password)
                                    time.sleep(2)

                                    original_url = driver.current_url

                                    # login_button_element.click()
                                    password_input_elem.send_keys(Keys.ENTER)

                                    # wait for screen to change where checkboxes of all cards you want to authorize shows

                                    if "americanexpress.com" in driver.current_url:
                                        WebDriverWait(driver, 15).until(
                                            EC.presence_of_element_located(
                                                (By.CSS_SELECTOR, "input[type='checkbox']")
                                            )
                                        )
                                    elif "citi.com" in driver.current_url:
                                        WebDriverWait(driver, 15).until(
                                            EC.presence_of_element_located(
                                                (By.CSS_SELECTOR, ".cds-checkbox:has(input.cds-checkbox-input[type='checkbox'])")
                                            )
                                        )

                                    # select all cards
                                    print("Selecting all cards...")

                                    if "americanexpress.com" in driver.current_url:
                                        checkbox_elems = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
                                    elif "citi.com" in driver.current_url:
                                        checkbox_elems = driver.find_elements(By.CSS_SELECTOR, ".cds-checkbox:has(input.cds-checkbox-input[type='checkbox'])")

                                    for checkbox_elem in checkbox_elems:
                                        actions = ActionChains(driver)
                                        actions.scroll_to_element(checkbox_elem)
                                        actions.perform()

                                        checkbox_elem.click()
                                        time.sleep(2)

                                    # click submit button
                                    # this selector works for both Amex and Citi
                                    authorize_button = driver.find_element(By.XPATH, "//button[text()[contains(., 'Authorize')]]")
                                    actions = ActionChains(driver)
                                    actions.scroll_to_element(authorize_button)
                                    actions.perform()

                                    driver.execute_script(
                                        "console.clear();"
                                    )  # clear JavaScript console log
                                    driver.execute_script("window.logs = [];")  # clear global var

                                    authorize_button.click()
                                    time.sleep(2)

                                    # for Amex, an additional screen appears before refresh
                                    # for Citi, this screen does not appear and refresh begins immediately
                                    if "americanexpress.com" in driver.current_url:
                                        # DOM updates here, so make sure to wait
                                        # then click return to Inuit button
                                        return_button = WebDriverWait(driver, 15).until(
                                            EC.presence_of_element_located(
                                                (By.XPATH, "//button[text()[contains(., 'Return')]]")
                                            )
                                        )

                                        actions = ActionChains(driver)
                                        actions.scroll_to_element(return_button)
                                        actions.perform()

                                        driver.execute_script(
                                            "console.clear();"
                                        )  # clear JavaScript console log
                                        driver.execute_script("window.logs = [];")  # clear global var

                                        return_button.click()
                                        time.sleep(2)

                                    # the window should automatically close and the normal refresh should happen now
                                    # for both Amex and Citi
                                    refresh_alread_initiated_and_console_cleared = True
                                    break
                        finally:
                            # at least for Amex and Citi, the window is automatically closed, so don't need to close manually
                            # if switched_windows:
                            #     driver.close()
                            driver.switch_to.window(original_window_handle)

                except:
                    traceback.print_exc()
                    print("Likely no reconnect needed")


                print(f"Refreshing account {account_name}")
                try:
                    if not refresh_alread_initiated_and_console_cleared:
                        if error_notification_elem and "verify your info" in error_notification_elem.text.lower():
                            reconnect_button1 = account_elem.find_element(By.CSS_SELECTOR, "button.fdx-mc-error-notification-action")
                            actions = ActionChains(driver)
                            actions.scroll_to_element(reconnect_button1)
                            actions.perform()

                            # DOM reloads here, so wait for mobile MFA radio button
                            # mobile_mfa_radio_button = WebDriverWait(driver, 15).until(
                            #     EC.presence_of_element_located(
                            #         (By.CSS_SELECTOR, "label[for='fdx-mfa-0-0'] .fdx-radio-label")
                            #     )
                            # )
                            # actions = ActionChains(driver)
                            # actions.scroll_to_element(mobile_mfa_radio_button)
                            # actions.perform()

                            # mobile_mfa_radio_button.click()
                            # time.sleep(2)

                            # reconnect_button2 = WebDriverWait(driver, 15).until(
                            #     EC.presence_of_element_located(
                            #         (By.CSS_SELECTOR, "button[aria-label='Connect']")
                            #     )
                            # )
                            # actions = ActionChains(driver)
                            # actions.scroll_to_element(reconnect_button2)
                            # actions.perform()
                        else:
                            more_options_button = account_elem.find_element(
                                By.CSS_SELECTOR, "button[aria-label='More Options']"
                            )
                            actions = ActionChains(driver)
                            actions.scroll_to_element(more_options_button)
                            actions.perform()
                            more_options_button.click() # click intercepted exception here sometimes here sometimes, though handled by try block to try agian
                            time.sleep(1)

                            refresh_button_elem = WebDriverWait(driver, 15).until(
                                EC.presence_of_element_located(
                                    (By.XPATH, "//li/span[contains(text(),'Refresh')]")
                                )
                            )
                            actions = ActionChains(driver)
                            actions.scroll_to_element(refresh_button_elem)
                            actions.perform()

                        driver.execute_script(
                            "console.clear();"
                        )  # clear JavaScript console log
                        driver.execute_script("window.logs = [];")  # clear global var

                        if error_notification_elem and "verify your info" in error_notification_elem.text.lower():
                            reconnect_button1.click()
                            time.sleep(2)
                            # reconnect_button2.click()
                            # time.sleep(2)
                        else:
                            refresh_button_elem.click()
                            time.sleep(2)

                    try:
                        # handle refresh sequence
                        search_str_list = [
                            '"connectionStatus":"SUCCESS"',
                            '"connectionStatus": "SUCCESS"',
                            "'connectionStatus':'SUCCESS'",
                            "'connectionStatus': 'SUCCESS'",
                            '"connectionStatus":"MFA"',
                            '"connectionStatus": "MFA"',
                            "'connectionStatus':'MFA'",
                            "'connectionStatus': 'MFA'",
                        ]
                        log_entry = WebDriverWait(driver, 120, 3).until( # exception here sometimes, though handled by try block to try agian
                            lambda driver: does_log_contain_any_string(
                                driver, search_str_list
                            )
                        )

                        search_str_list = [
                            '"connectionStatus":"MFA"',
                            '"connectionStatus": "MFA"',
                            "'connectionStatus':'MFA'",
                            "'connectionStatus': 'MFA'",
                        ]
                        mfa_status_in_log = does_log_contain_any_string(
                            driver, search_str_list
                        )

                        security_info_required_elem = None
                        if mfa_status_in_log:
                            print(
                                "MFA in console. Waiting 5 seconds then switching to default frame..."
                            )
                            time.sleep(5)
                            driver.switch_to.default_content()

                            # wait for at least 1 iframe
                            WebDriverWait(driver, 60).until(
                                lambda driver: driver.execute_script(
                                    "return frames.length"
                                )
                                > 0
                            )

                            # switch to correct iframe that contains the security info required element elem below
                            # note it is a nested one, so need to switch frames 2 or more times
                            security_info_required_elem = None
                            parent_frames_length = driver.execute_script(
                                "return frames.length"
                            )
                            for i in range(parent_frames_length):
                                driver.switch_to.frame(i)

                                # likely not in parent iframe, but check in case of website redesign
                                try:
                                    security_info_required_elem = WebDriverWait(
                                        driver, 10
                                    ).until(
                                        EC.presence_of_element_located(
                                            (
                                                By.CSS_SELECTOR,
                                                "div[aria-label='Header: Security info required']",
                                            )
                                        )
                                    )
                                except:
                                    pass

                                if security_info_required_elem is not None:
                                    print(
                                        f"Found security info required element elem in parent frame {i}"
                                    )
                                    break

                                child_frames_length = driver.execute_script(
                                    "return frames.length"
                                )
                                if child_frames_length > 0:
                                    for i2 in range(child_frames_length):
                                        driver.switch_to.frame(i2)
                                        try:
                                            security_info_required_elem = WebDriverWait(
                                                driver, 10
                                            ).until(
                                                EC.presence_of_element_located(
                                                    (
                                                        By.CSS_SELECTOR,
                                                        "div[aria-label='Header: Security info required']",
                                                    )
                                                )
                                            )
                                        except:
                                            pass

                                        if security_info_required_elem is not None:
                                            print(
                                                f"Found security info required element elem in parent frame {i}, child frame {i2}"
                                            )
                                            break

                                if security_info_required_elem is not None:
                                    break

                            if security_info_required_elem is None:
                                driver.switch_to.default_content()
                                raise Exception(
                                    "Could not find security info required element in any iframe"
                                )

                        if security_info_required_elem is not None or mfa_status_in_log:
                            print("MFA required")

                            child_username = get_child_username(PARENT_CREDENTIAL_ACCOUNT, parent_username, account_name)

                            if not child_username:
                                raise Exception(f"Unable to find child username for {account_name} under parent {PARENT_CREDENTIAL_ACCOUNT}")

                            update_otp(account_name, child_username, "")

                            text_to_phone_number_radio_button_label_elem = (
                                WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located(
                                        (By.CSS_SELECTOR, ".fdx-radio-label")
                                    )
                                )
                            )
                            actions = ActionChains(driver)
                            actions.scroll_to_element(
                                text_to_phone_number_radio_button_label_elem
                            )
                            actions.perform()
                            text_to_phone_number_radio_button_label_elem.click()
                            time.sleep(2)

                            connect_button = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located(
                                    (By.CSS_SELECTOR, "button[aria-label='Connect']")
                                )
                            )
                            actions = ActionChains(driver)
                            actions.scroll_to_element(connect_button)
                            actions.perform()
                            connect_button.click()
                            print("Initiated SMS code send procedure")
                            time.sleep(3)

                            print(
                                "Waiting for actual SMS code input page to sign in..."
                            )
                            WebDriverWait(driver, 20).until(
                                EC.text_to_be_present_in_element(
                                    (By.CSS_SELECTOR, ".fdx-input-group-label"),
                                    "Please enter the one time code",
                                )
                            )

                            sms_code_input_element = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located(
                                    (By.CSS_SELECTOR, "input#fdx-mfa-0")
                                )
                            )

                            print(
                                "Found SMS code input. Waiting for SMS forwarder app and Flask server to retrieve code..."
                            )
                            # wait for global otp to not be empty -- Flask thread should set it
                            try:
                                WebDriverWait(driver, 30).until(
                                    lambda driver: get_otp(account_name, child_username) != ""
                                )
                            except:
                                traceback.print_exc()
                                print("Did not get SMS code")

                            if get_otp(account_name, child_username) == "":
                                raise Exception("Did not get SMS code")
                            else:
                                print(
                                    f"Retrieved code {get_otp(account_name, child_username)}. Attempting sign in with it..."
                                )

                                time.sleep(1)
                                sms_code_input_element.send_keys(
                                    get_otp(account_name, child_username)
                                )
                                time.sleep(1)

                                # enter key does not work here, so need to click Connect button
                                connect_button = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located(
                                        (
                                            By.CSS_SELECTOR,
                                            "button[aria-label='Connect']",
                                        )
                                    )
                                )
                                actions = ActionChains(driver)
                                actions.scroll_to_element(connect_button)
                                actions.perform()

                                driver.execute_script(
                                    "console.clear();"
                                )  # clear JavaScript console log
                                driver.execute_script(
                                    "window.logs = [];"
                                )  # clear global var

                                connect_button.click()
                                print("Initiated SMS code send procedure")
                                time.sleep(3)

                                # handle refresh sequence
                                search_str_list = [
                                    '"connectionStatus":"SUCCESS"',
                                    '"connectionStatus": "SUCCESS"',
                                    "'connectionStatus':'SUCCESS'",
                                    "'connectionStatus': 'SUCCESS'",
                                ]
                                log_entry = WebDriverWait(driver, 120, 3).until(
                                    lambda driver: does_log_contain_any_string(
                                        driver, search_str_list
                                    )
                                )

                                print("Successful MFA sign in")

                        add_db_record(
                            cursor, parent_username, account_name, "REFRESHED", str(log_entry)
                        )
                        print(f"Refresh successful. Log entry found: {str(log_entry)}")
                        time.sleep(3)

                        failed_attempt -= 1
                        need_refresh = True
                        break  # need to exit loop because elements will be stale now
                    except:
                        traceback.print_exc()
                        print("Problem refreshing account")

                        db_info = "Exception while refreshing"
                        try:
                            notification_detail_elem = driver.find_element(
                                By.CSS_SELECTOR, ".fdx-notification-detail"
                            )
                            notification_detail_text = (
                                notification_detail_elem.get_attribute("textContent")
                            )
                            
                            if notification_detail_text:
                                extra_message = f"Notification detail text: {notification_detail_text}"
                                print(extra_message)
                                db_info += f" {extra_message}"

                            if "Please try again later" in notification_detail_text:
                                print(
                                    "Notification detail shows we need to try again later"
                                )
                        finally:
                            add_db_record(
                                cursor,
                                parent_username,
                                account_name,
                                "ERROR",
                                db_info,
                            )

                        close_button = driver.find_element(
                            By.CSS_SELECTOR, "button[aria-label='Close']"
                        )
                        close_button.click()
                        time.sleep(2)

                        # this will actually reload the page, so all elements will become stale and we need to refresh them
                        error = True
                        break
                except:
                    traceback.print_exc()
                    add_db_record(
                        cursor,
                        parent_username,
                        account_name,
                        "ERROR",
                        "Exception while refreshing",
                    )

                    print("Navigating to linked accounts page...")
                    driver.get("https://www.creditkarma.com/connect/manage-accounts")
                    try:
                        driver.execute_script(
                            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
                        )
                    except:
                        pass
                    time.sleep(2)

                    # this will actually reload the page, so all elements will become stale and we need to refresh them
                    error = True
                    break

            # a break here is needed when all accounts have attempted to be refreshed
            if not error and not need_refresh:
                break
