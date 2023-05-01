from core import *
from selenium.webdriver.common.by import By
import winsound
import undetected_chromedriver as uc
import time
import os
import glob
import threading


options = uc.ChromeOptions()
# options.add_argument("--headless")
options.add_argument("--start-maximized")
options.add_argument("--disable-features=VizDisplayCompositor")  # Attempt to fix issue where screenshots aren't working
if is_incognito:
    options.add_argument("--incognito")  # Toggle this when Error 15 appears
# options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
#                     "Chrome/111.0.0.0 Safari/537.36")

with Fragile(Chrome(options=options, version_main=111)) as driver:
    execute_with_retry(retries, try_get_url, target_url, "0.00", driver)

    if should_pause_on_start:
        play_song("0.01", paused_sound_loop, winsound.SND_ASYNC + winsound.SND_LOOP)
        input("Paused. Press enter to continue when the page is ready (Step 1)...")
        stop_song("0.02")

    # Step 1 Page
    captcha_code_1, captcha_code_2, captcha_code_3, captcha_code_4 = "1.00", "1.01", "1.02", "1.03"
    kill_thread = False
    watcher = threading.Thread(target=pause_if_captcha_page_watcher, args=(driver,))
    watcher.start()
    # Wait for sub-thread to check page
    if not should_pause_on_start:
        time.sleep(get_random_delay_or_median(page_load_delay_range_1, page_load_delay_range_2))

    # execute_with_retry(retries, quit_if_title_mismatch, "Access your booking - Change booking", "1.10", "1.11",
    # driver)

    step_one_licence_form = execute_with_retry(
        retries, get_el_by_attribute_else_quit, "username", "1.20", By.NAME, driver)

    execute_with_retry(retries, click_el_else_quit, "Licence Input", step_one_licence_form, "1.21", driver)

    time.sleep(get_random_delay_or_median(form_delay_range_1, form_delay_range_2))
    execute_with_retry(
        retries, fill_text_input_else_quit, "Licence Input", step_one_licence_form, licence_no, "1.22", driver)

    step_one_licence_ref_no_form = execute_with_retry(
        retries, get_el_by_attribute_else_quit, "password", "1.30", By.NAME, driver)

    execute_with_retry(
        retries, click_el_else_quit, "Licence Ref No Input", step_one_licence_ref_no_form, "1.31", driver)

    time.sleep(get_random_delay_or_median(form_delay_range_1, form_delay_range_2))
    execute_with_retry(
        retries, fill_text_input_else_quit,
        "Licence Ref No Input", step_one_licence_ref_no_form, test_ref_no, "1.32", driver)

    step_one_btn = execute_with_retry(
        retries, get_el_by_attribute_else_quit, "booking-login", "1.40", By.NAME, driver)

    execute_with_retry(retries, verify_submit_btn_el_else_quit, step_one_btn, "1.41", driver)

    time.sleep(get_random_delay_or_median(submit_delay_range_1, submit_delay_range_2))
    execute_with_retry(retries, click_el_else_quit, "Submit Btn", step_one_btn, "1.42", driver)

    # Step 2 Page
    set_captcha_codes("2.00", "2.01", "2.02", "2.03")
    time.sleep(get_random_delay_or_median(page_load_delay_range_1, page_load_delay_range_2))

    # execute_with_retry(retries, quit_if_title_mismatch, "Booking details - Change booking", "2.10", "2.11", driver)

    step_two_btn = execute_with_retry(retries, get_el_by_attribute_else_quit, "date-time-change", "2.20", By.ID, driver)

    time.sleep(get_random_delay_or_median(submit_delay_range_1, submit_delay_range_2))
    execute_with_retry(retries, click_el_else_quit, "Change Booking Date Time Btn", step_two_btn, "2.21", driver)

    # Step 3 Page
    set_captcha_codes("3.00", "3.01", "3.02", "3.03")
    time.sleep(get_random_delay_or_median(page_load_delay_range_1, page_load_delay_range_2))

    # execute_with_retry(retries, quit_if_title_mismatch, "Test date - Change booking", "3.10", "3.11", driver)

    step_three_test_choice_form = execute_with_retry(
        retries, get_el_by_attribute_else_quit, "test-choice-earliest", "3.20", By.ID, driver)

    time.sleep(get_random_delay_or_median(form_delay_range_1, form_delay_range_2))
    execute_with_retry(
        retries, click_el_else_quit, "Test Choice Earliest Radio Btn", step_three_test_choice_form, "3.21", driver)

    step_three_btn = execute_with_retry(
        retries, get_el_by_attribute_else_quit, "drivingLicenceSubmit", "3.30", By.NAME, driver)

    execute_with_retry(retries, verify_submit_btn_el_else_quit, step_three_btn, "3.31", driver)

    time.sleep(get_random_delay_or_median(submit_delay_range_1, submit_delay_range_2))
    execute_with_retry(retries, click_el_else_quit, "Submit Btn", step_three_btn, "3.32", driver)

    # Step 4 Page
    set_captcha_codes("4.00", "4.01", "4.02", "4.03")
    while True:
        time.sleep(get_random_delay_or_median(page_load_delay_range_1, page_load_delay_range_2))

        # execute_with_retry(retries, quit_if_title_mismatch, "Test date / time — test times available - Change
        # booking", "4.10", "4.11", driver)

        if is_el_found_by_xpath(
                "Bookable Calendar Btn", "4.20", "//td[@class='BookingCalendar-date--bookable ']", driver):
            step_six_calendar_btn = execute_with_retry(
                retries, get_el_by_xpath_else_quit,
                "Calendar Btn", "4.21", "//td[@class='BookingCalendar-date--bookable ']/div/a", driver)

            if verify_attribute_href_date_is_earlier(test_date, step_six_calendar_btn, "4.30", driver):
                logger.debug("4.31a - Found an earlier date!!!")
                play_song("4.31" + "M", available_booking_sound)
                break
            else:
                logger.debug("4.31b - No *earlier* date. URL: " + driver.current_url + " --- Refreshing the browser...")
        else:
            logger.debug("4.21 - No bookable calendar buttons --- Refreshing the browser...")

        if is_el_found_by_xpath("Search Limit Reached Page", "4.32", "//*[@id='main']/header/h1",
                                driver) or is_el_found_by_xpath(
                "Modal Window Visible",
                "4.33", "//div[@class='underlay' and @style='display: block;']", driver):
            logger.error("444" + " - " + "On Search Limit Reached Page/Modal, now quitting when browser dies...")
            try_screenshot("4.34", "On Search Limit Reached Page/Modal", driver)
            play_song("999X", captcha_sound_loop, winsound.SND_ASYNC + winsound.SND_LOOP)
            # Quit the browser instance if browser dies
            sleep_while_browser_alive("999", driver)
            logger.debug("Killing process...")
            kill_thread = True
            raise Fragile.Break

        execute_with_retry(retries, try_get_url,
                           "https://driverpracticaltest.dvsa.gov.uk/manage?execution=e1s2",
                           "4.40", driver)
        time.sleep(get_random_delay_or_median(page_load_delay_range_1, page_load_delay_range_2))

        # execute_with_retry(retries, quit_if_title_mismatch, "Test date - Change booking", "4.40", "4.41", driver)

        step_three_btn = execute_with_retry(
            retries, get_el_by_attribute_else_quit, "drivingLicenceSubmit", "4.50", By.NAME, driver)

        execute_with_retry(retries, verify_submit_btn_el_else_quit, step_three_btn, "4.51", driver)

        time.sleep(get_random_delay_or_median(submit_delay_range_1, submit_delay_range_2))
        execute_with_retry(retries, click_el_else_quit, "Submit Btn", step_three_btn, "4.52", driver)

    time.sleep(get_random_delay_or_median(form_delay_range_1, form_delay_range_2))
    execute_with_retry(retries, click_el_else_quit, "Calendar Btn", step_six_calendar_btn, "4.60", driver)
    time.sleep(1)  # Wait briefly for radio buttons to load

    step_six_timeslot_btn = execute_with_retry(
        retries, get_el_by_xpath_else_quit,
        "Time Slot Btn", "4.61", "//li[@class='SlotPicker-day is-active']/label", driver)

    time.sleep(get_random_delay_or_median(form_delay_range_1, form_delay_range_2))
    execute_with_retry(retries, click_el_else_quit, "Time Slot Btn", step_six_timeslot_btn, "4.62", driver)

    step_six_submit_btn = execute_with_retry(
        retries, get_el_by_attribute_else_quit, "chooseSlotSubmit", "4.70", By.NAME, driver)

    execute_with_retry(retries, verify_submit_btn_el_else_quit, step_six_submit_btn, "4.71", driver)

    time.sleep(get_random_delay_or_median(form_delay_range_1, form_delay_range_2))
    execute_with_retry(retries, click_el_else_quit, "Submit Btn", step_six_submit_btn, "4.72", driver)

    on_modal_screen = execute_with_retry(
        retries, get_el_by_xpath_else_quit,
        "Modal Window Visible", "4.80", "//div[@class='underlay-wrapper' and @style='display: block;']", driver, 25, 3)

    # Wait briefly on modal screen to try and avoid being kicked off (unneeded?)
    time.sleep(get_random_delay_or_median(form_delay_range_1, form_delay_range_2))
    step_five_timeslot_modal_btn = execute_with_retry(
        retries, get_el_by_xpath_else_quit, "Time Continue Btn", "4.81",
        "//div[@class='underlay-wrapper']/div/section/div/div[@class='dialog-wrapper-inner']/div/button", driver)

    execute_with_retry(
        retries, click_el_else_quit, "Time Continue Btn", step_five_timeslot_modal_btn, "4.82", driver)

    # Step 5 Page - wait for user to do the rest
    set_captcha_codes("5.00", "5.01", "5.02", "5.03")
    time.sleep(get_random_delay_or_median(page_load_delay_range_1, page_load_delay_range_2))

    play_song("5.10M", final_step_loop, winsound.SND_ASYNC + winsound.SND_LOOP)

    while True:
        try:
            logger.debug("5.11a - Waiting on confirm page indefinitely...")
        except Exception as ex:
            log_err(ex, "5.11b", "Error while waiting on confirm page for user indefinitely. Waiting until "
                                 "browser dies...")
            # Quit the browser instance if browser dies
            stop_song("5.12M")
            sleep_while_browser_alive("999", driver)
            logger.debug("Killing process...")
            kill_thread = True
            raise Fragile.Break
        time.sleep(300)

logger.debug("Killed process.")

file_handler.close()
files = glob.glob(working_dir + "/logs/*")
for f in files:
    if not os.path.getsize(f):
        os.remove(f)

if not manual_restart:
    restart_program(logger)
