from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import undetected_chromedriver as uc
import time
import os
import glob
import traceback
import threading
import signal
import logging
from logging.handlers import RotatingFileHandler


def sleep_while_browser_alive(code, browser):
    logger.debug(code + " - Continuously checking if browser is alive...")
    continue_app = True
    while continue_app:
        try:
            _ = browser.window_handles
            time.sleep(1)
        except Exception as exc:
            log_err(exc, code + "a", "Browser is no longer alive")
            continue_app = False


class Chrome(uc.Chrome):
    # Override exit to not restart service or start() and remove sleep
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.service.stop()


def namer(name):
    return name.replace(".log", "") + ".log"


class Fragile(object):
    class Break(Exception):
        """Break out of the with statement"""

    def __init__(self, value):
        self.value = value

    def __enter__(self):
        return self.value.__enter__()

    def __exit__(self, etype, value, traceback):
        error = self.value.__exit__(etype, value, traceback)
        if etype == self.Break:
            return True
        return error


def close_and_kill(browser):
    global kill_thread
    logger.debug("Killing process...")
    kill_thread = True
    browser.quit()
    raise Fragile.Break


def try_screenshot(code, message, browser):
    try:
        logger.debug(code + "S - Now taking screenshot for msg: " + message + "...")
        browser.save_screenshot("screenshots/" + time.strftime("%Y.%m.%d - %H.%M.%S - ") + code + ".png")
        logger.debug(code + "S1 - Screenshot captured for msg: " + message)
    except SubThreadException:
        raise SubThreadException
    except Exception as exc:
        log_err(exc, code + "S2", "Failed to take screenshot for msg: " + message)


def log_err(error, code, message):
    logger.debug(code + " - " + type(error).__name__ + ": " + message)
    logger.error(code + " - " + traceback.format_exc())


def handle_err_and_quit(error, code, message, browser):
    # try_screenshot(code, message, browser)
    logger.debug(code + " - " + type(error).__name__ + ": " + message)
    logger.error(code + " - " + traceback.format_exc())
    close_and_kill(browser)


def pause_if_captcha_page_watcher(browser):
    while True:
        if kill_thread:
            return
        time.sleep(1)
        logger.debug(captcha_code_1 + " - Checking if captcha page...")
        if is_el_found_by_attribute_single_check("error-content", captcha_code_1, By.CLASS_NAME, browser):
            os.kill(os.getpid(), signal.SIGUSR1)  # Throw SubThreadException in main thread via signal
            logger.debug(captcha_code_2 + "a - Confirmed on captcha page. Waiting for user to continue execution...")
            input("Press enter to continue execution when page is ready...")

            logger.debug(captcha_code_3 + " - Continuing execution...")
        else:
            logger.debug(captcha_code_3 + "b - Not on captcha page. Continuing execution...")


def set_captcha_codes(code1, code2, code3):
    global captcha_code_1, captcha_code_2, captcha_code_3
    captcha_code_1 = code1
    captcha_code_2 = code2
    captcha_code_3 = code3


def is_el_found_by_attribute_single_check(name, code, by_attr, browser):
    try:
        logger.debug(code + " - Now capturing element by " + str(by_attr) + "...")
        element = browser.find_element(by=by_attr, value=name)
        logger.debug(code + "a - Element captured by " + str(by_attr) + ". Element is: " + str(element))
        return True
    except NoSuchElementException as exc:
        logger.error(code + "b" + " - " + type(exc).__name__ + ": " + "Element was not found by " + str(by_attr))
        return False
    except SubThreadException:
        raise SubThreadException
    except Exception as exc:
        handle_err_and_quit(exc, code + "c", "Failed to capture element by " + str(by_attr), browser)


def try_get_url(url, code, browser):
    try:
        logger.debug(code + " - Now reaching target URL...")
        browser.get(url)
        logger.debug(code + "a - Successfully reached target URL")
    except SubThreadException:
        raise SubThreadException
    except Exception as exc:
        handle_err_and_quit(exc, code + "b", "Failed to reach target URL", browser)


def quit_if_title_mismatch(title, code1, code2, browser):
    try:
        logger.debug(code1 + " - Now getting page title...")
        get_title = browser.title
        logger.debug(code1 + "a - Successfully got page title")
    except SubThreadException:
        raise SubThreadException
    except Exception as exc:
        handle_err_and_quit(exc, code1 + "b", "Failed to get page title", browser)

    try:
        logger.debug(code2 + " - Now checking if page title matches...")
        if get_title == title:
            logger.debug(code2 + "a - Title is as expected")
        else:
            raise ValueError()
    except ValueError as exc:
        handle_err_and_quit(exc, code2 + "b", "Title not as expected. Expected: " +
                            title + " || Actual: " + get_title, browser)
    except SubThreadException:
        raise SubThreadException
    except Exception as exc:
        handle_err_and_quit(exc, code2 + "c", "Failed to check if page title matches", browser)


def is_el_found_by_attribute(name, code, by_attr, browser, timeout=5, polling=0.5):
    try:
        logger.debug(code + " - Now capturing element by " + str(by_attr) + "...")
        element = WebDriverWait(browser, timeout, polling).until(lambda d: d.find_element(by=by_attr, value=name))
        logger.debug(code + "a - Element captured by " + str(by_attr) + ". Element is: " + str(element))
        return True
    except TimeoutException as exc:
        log_err(exc, code + "b", "Element was not found by " + str(by_attr))
        return False
    except SubThreadException:
        raise SubThreadException
    except Exception as exc:
        handle_err_and_quit(exc, code + "c", "Failed to capture element by " + str(by_attr), browser)


def get_el_by_attribute_else_quit(name, code, by_attr, browser, timeout=5, polling=0.5):
    try:
        logger.debug(code + " - Now capturing element by " + str(by_attr) + "...")
        element = WebDriverWait(browser, timeout, polling).until(lambda d: d.find_element(by=by_attr, value=name))
        logger.debug(code + "a - Element captured by " + str(by_attr) + ". Element is: " + str(element))
        return element
    except TimeoutException as exc:
        handle_err_and_quit(exc, code + "b", "Element was not found by " + str(by_attr), browser)
    except SubThreadException:
        raise SubThreadException
    except Exception as exc:
        handle_err_and_quit(exc, code + "c", "Failed to capture element by " + str(by_attr), browser)


def verify_submit_btn_el_else_quit(element, code, browser):
    try:
        logger.debug(code + " - Now verifying submit btn element...")
        if element.get_attribute("class") == "button" and element.get_attribute("type") == "submit":
            logger.debug(code + "a - Element is submit btn as expected")
        else:
            raise ValueError()
    except ValueError as exc:
        handle_err_and_quit(exc, code + "b", "Element is not submit btn as expected.", browser)
    except SubThreadException:
        raise SubThreadException
    except Exception as exc:
        handle_err_and_quit(exc, code + "c", "Failed to verify submit btn element", browser)


def click_el_else_quit(name, element, code, browser):
    try:
        logger.debug(code + " - Now clicking on " + name + " element...")
        element.click()
        logger.debug(code + "a - Successfully clicked on " + name + " element")
    except SubThreadException:
        raise SubThreadException
    except Exception as exc:
        handle_err_and_quit(exc, code + "b", "Failed to click on " + name + " element", browser)


def fill_text_input_else_quit(name, element, txt_input, code, browser):
    try:
        logger.debug(code + " - Now filling in " + name + " text field...")
        element.send_keys(txt_input)
        logger.debug(code + "a - Successfully clicked on " + name + " element")
    except SubThreadException:
        raise SubThreadException
    except Exception as exc:
        handle_err_and_quit(exc, code + "b", "Failed to fill in " + name + " text field", browser)


def try_catch_sub_thread_exc(retry_count, browser, fun, *args, **kwargs):
    try:
        result = fun(*args, **kwargs)
        return result
    except SubThreadException as exc:
        logger.debug("444 - " + str(exc) + ": Paused main thread. Waiting for user to continue execution...")
        input("Press enter to continue main thread execution when page is ready...")
        logger.debug("444 - Continuing execution...")
        if retry_count > 0:
            retry_count -= 1
            logger.debug("444 - Retrying last function executed. Retries remaining: " + retry_count)
            try_catch_sub_thread_exc(retry_count, fun, *args, **kwargs)  # If captcha page is resolved, retry last call
        else:
            handle_err_and_quit(exc, "444", "No retries left on last function executed. Quitting...", browser)
    except Fragile.Break:
        raise Fragile.Break


class SubThreadException(Exception):
    pass


def usr1_handler():
    raise SubThreadException()


signal.signal(signal.SIGUSR1, usr1_handler)

file_time = time.strftime("%Y.%m.%d - %H.%M.%S")
logger = logging.getLogger("Rotating Log")
logger.root.setLevel(logging.NOTSET)
handler = RotatingFileHandler("logs/" + file_time + "-debug.log", maxBytes=1000000, backupCount=10)
handler.namer = namer
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

target_url = "https://driverpracticaltest.dvsa.gov.uk/application"
license_no = "MORGA657054SM9IJ"

options = uc.ChromeOptions()
# options.add_argument("--headless")
options.add_argument("--start-maximized")
options.add_argument("--incognito")
# options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
#                     "Chrome/111.0.0.0 Safari/537.36")

with Fragile(Chrome(options=options, version_main=111)) as driver:
    retries = 3
    try_catch_sub_thread_exc(retries, driver, try_get_url, target_url, "0.00", driver)

    # Step 1 Page
    captcha_code_1, captcha_code_2, captcha_code_3 = "1.00", "1.01", "1.02"
    kill_thread = False
    watcher = threading.Thread(target=pause_if_captcha_page_watcher, args=(driver,))
    watcher.start()
    time.sleep(2)  # Wait for sub-thread to check page

    try_catch_sub_thread_exc(retries, driver, quit_if_title_mismatch, "Type of test", "1.10", "1.11", driver)

    step_one_btn = try_catch_sub_thread_exc(retries, driver,
                                            get_el_by_attribute_else_quit, "testTypeCar", "1.20", By.NAME, driver)

    try_catch_sub_thread_exc(retries, driver, verify_submit_btn_el_else_quit, step_one_btn, "1.21", driver)

    try_catch_sub_thread_exc(retries, driver, click_el_else_quit, "Submit Btn", step_one_btn, "1.22", driver)

    # Step 2 Page
    set_captcha_codes("2.00", "2.01", "2.02")

    try_catch_sub_thread_exc(retries, driver, quit_if_title_mismatch, "License details", "2.10", "2.11", driver)

    step_two_license_form = try_catch_sub_thread_exc(
        retries, driver, get_el_by_attribute_else_quit, "driverLicenceNumber", "2.20", By.NAME, driver)

    try_catch_sub_thread_exc(retries, driver,
                             click_el_else_quit, "License Input", step_two_license_form, "2.21", driver)

    try_catch_sub_thread_exc(retries, driver,
                             fill_text_input_else_quit, "License Input", step_two_license_form,
                             license_no, "2.22", driver)

    step_two_special_needs_form = try_catch_sub_thread_exc(
        retries, driver, get_el_by_attribute_else_quit, "special-needs-none", "2.30", By.ID, driver)

    try_catch_sub_thread_exc(retries, driver,
                             click_el_else_quit, "Special Needs Radio Btn", step_two_special_needs_form, "2.31", driver)

    step_two_btn = try_catch_sub_thread_exc(
        retries, driver, get_el_by_attribute_else_quit, "drivingLicenceSubmit", "2.32", By.NAME, driver)

    try_catch_sub_thread_exc(retries, driver, verify_submit_btn_el_else_quit, step_two_btn, "2.40", driver)

    try_catch_sub_thread_exc(retries, driver, click_el_else_quit, "Submit Btn", step_two_btn, "2.41", driver)

    # Step 3 Page
    # TODO

    # Quit the browser instance
    sleep_while_browser_alive("999", driver)
    logger.debug("Killing process...")
    kill_thread = True
    raise Fragile.Break

logger.debug("Killed process.")

handler.close()
files = glob.glob('logs/*')
for f in files:
    if not os.path.getsize(f):
        os.remove(f)
