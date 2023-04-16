from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import undetected_chromedriver as uc
import time
import os
import glob
import traceback
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
            logger.debug(code + "a - " + type(exc).__name__ + ": " + "Browser is no longer alive")
            logger.error(code + "a - " + traceback.format_exc())
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
    logger.debug("Killing process...")
    browser.quit()
    raise Fragile.Break


def handle_err_and_quit(error, code, message, browser):
    logger.debug(code + " - " + type(error).__name__ + ": " + message)
    logger.error(code + " - " + traceback.format_exc())
    close_and_kill(browser)


def try_get_url(url, code, browser):
    try:
        logger.debug(code + " - Now reaching target URL...")
        browser.get(url)
        logger.debug(code + "a - Successfully reached target URL")
    except Exception as exc:
        handle_err_and_quit(exc, code, "Failed to reach target URL", browser)


def quit_if_title_mismatch(title, code1, code2, browser):
    try:
        logger.debug(code1 + " - Now getting page title...")
        get_title = browser.title
        logger.debug(code1 + "a - Successfully got page title")
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
    except Exception as exc:
        handle_err_and_quit(exc, code2 + "c", "Failed to check if page title matches", browser)


def get_el_by_name_else_quit(name, code, browser, timeout=5):
    try:
        logger.debug(code + " - Now capturing element by name...")
        element = WebDriverWait(browser, timeout=timeout).until(lambda d: d.find_element(by=By.NAME, value=name))
        logger.debug(code + "a - Element captured by name. Element is: " + str(element))
        return element
    except TimeoutException as exc:
        handle_err_and_quit(exc, code + "b", "Element was not found by name", browser)
    except Exception as exc:
        handle_err_and_quit(exc, code + "c", "Failed to capture element by name", browser)


def verify_submit_btn_el_else_quit(element, code, browser):
    try:
        logger.debug(code + " - Now verifying submit btn element...")
        if element.get_attribute("class") == "button" and element.get_attribute("type") == "submit":
            logger.debug(code + "a - Element is submit btn as expected")
        else:
            raise ValueError()
    except ValueError as exc:
        handle_err_and_quit(exc, code + "b", "Element is not submit btn as expected.", browser)
    except Exception as exc:
        handle_err_and_quit(exc, code + "c", "Failed to verify submit btn element", browser)


def click_btn_else_quit(element, code, browser):
    try:
        logger.debug(code + " - Now clicking on button...")
        element.click()
        logger.debug(code + "a - Successfully clicked on button")
    except Exception as exc:
        handle_err_and_quit(exc, code + "b", "Failed to click on button", browser)


file_time = time.strftime("%Y.%m.%d - %H.%M.%S")
logger = logging.getLogger("Rotating Log")
logger.root.setLevel(logging.NOTSET)
handler = RotatingFileHandler("logs/" + file_time + "-debug.log", maxBytes=1000000, backupCount=10)
handler.namer = namer
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

target_url = "https://driverpracticaltest.dvsa.gov.uk/application"

options = uc.ChromeOptions()
# options.add_argument("--headless")
options.add_argument("--start-maximized")
options.add_argument("--incognito")
# options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
#                     "Chrome/111.0.0.0 Safari/537.36")

with Fragile(Chrome(options=options, version_main=111)) as driver:
    try_get_url(target_url, "0.0", driver)
    input("Press enter to continue execution when page is ready...")
    # driver.save_screenshot("screenshot1.png")

    quit_if_title_mismatch("Type of test", "1.1", "1.2", driver)

    step_one_btn = get_el_by_name_else_quit("testTypeCar", "1.3", driver)

    verify_submit_btn_el_else_quit(step_one_btn, "1.4", driver)

    click_btn_else_quit(step_one_btn, "1.5", driver)

    # Quit the browser instance
    sleep_while_browser_alive("999", driver)
    logger.debug("Killing process...")
    raise Fragile.Break

logger.debug("Killed process.")

handler.close()
files = glob.glob('logs/*')
for f in files:
    if not os.path.getsize(f):
        os.remove(f)
