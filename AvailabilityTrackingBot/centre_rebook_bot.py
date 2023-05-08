from core import *
from selenium.webdriver.common.by import By
from selenium.webdriver import Keys
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

with Fragile(Chrome(options=options, version_main=113)) as driver:
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

    step_two_btn = execute_with_retry(
        retries, get_el_by_attribute_else_quit, "test-centre-change", "2.20", By.ID, driver)

    time.sleep(get_random_delay_or_median(submit_delay_range_1, submit_delay_range_2))
    execute_with_retry(retries, click_el_else_quit, "Change Booking Test Centre Btn", step_two_btn, "2.21", driver)

    # Step 3 Page
    set_captcha_codes("3.00", "3.01", "3.02", "3.03")
    time.sleep(get_random_delay_or_median(page_load_delay_range_1, page_load_delay_range_2))

    # execute_with_retry(retries, quit_if_title_mismatch, "Test date - Change booking", "3.10", "3.11", driver)

    step_three_postcode_form = execute_with_retry(
        retries, get_el_by_attribute_else_quit, "testCentreName", "3.20", By.NAME, driver)

    execute_with_retry(retries, click_el_else_quit, "Postcode Input", step_three_postcode_form, "3.21", driver)

    time.sleep(get_random_delay_or_median(form_delay_range_1, form_delay_range_2))
    execute_with_retry(retries, fill_text_input_else_quit, "Postcode Input", step_three_postcode_form,
                       Keys.CONTROL + "a", "3.22", driver)

    time.sleep(get_random_delay_or_median(form_delay_range_1, form_delay_range_2))
    execute_with_retry(retries, fill_text_input_else_quit, "Postcode Input", step_three_postcode_form,
                       Keys.DELETE, "3.23", driver)

    time.sleep(get_random_delay_or_median(form_delay_range_1, form_delay_range_2))
    execute_with_retry(
        retries, fill_text_input_else_quit, "Postcode Input", step_three_postcode_form, post_code_full, "3.24", driver)

    # Step 3.3 - Postcode Search & Loop

    keep_searching_centres = True
    while keep_searching_centres:
        time.sleep(get_random_delay_or_median(search_delay_range_1, search_delay_range_2))

        # Refresh postcode_form element target upon driver.refresh() each iteration
        step_three_postcode_form = execute_with_retry(
            retries, get_el_by_attribute_else_quit, "testCentreName", "3.30", By.NAME, driver)

        step_three_btn = execute_with_retry(
            retries, get_el_by_attribute_else_quit, "testCentreSubmit", "3.40", By.NAME, driver)

        execute_with_retry(retries, verify_submit_btn_el_else_quit, step_three_btn, "3.41", driver)

        # Try to navigate to the button by moving to page header
        step_three_header = execute_with_retry(
            retries, get_el_by_attribute_else_quit, "page-header", "3.42", By.CLASS_NAME, driver)

        execute_with_retry(
            retries, try_move_to_el_else_quit, "Page Header Submit Btn", step_three_header, "3.43", driver)

        execute_with_retry(retries, click_el_else_quit, "Submit Btn", step_three_btn, "3.50", driver)
        # Wait at least x seconds before checking the search results
        time.sleep(get_random_delay_or_median(page_load_delay_range_1, page_load_delay_range_2))

        search_results_exist = execute_with_retry(
            retries, is_el_found_by_attribute, "test-centre-content", "3.60", By.CLASS_NAME, driver, 25, 2.5)

        if search_results_exist:
            for i in test_centre_names:
                logger.debug("3.61 - Searching for an available booking at " + i + "...")
                step_three_test_el = execute_with_retry(
                    retries, get_el_by_tag_and_text_sibling_else_quit,
                    "Test Centre " + i + " Status Link", "3.62", "h4", i, "h5", driver)

                if execute_with_retry(
                        retries, is_el_text_matching,
                        "Test Centre " + i + " Status Message", step_three_test_el, "available", "3.63", driver):
                    play_song("3.63" + "M", available_booking_sound)
                    logger.debug("3.63a - Found an available booking at " + i + "!!!")
                    execute_with_retry(
                        retries, try_move_to_el_else_quit, "Booking Link", step_three_test_el, "3.64", driver)
                    execute_with_retry(retries, click_el_else_quit, "Booking Link", step_three_test_el, "3.65", driver)

                    time.sleep(get_random_delay_or_median(page_load_delay_range_1, page_load_delay_range_2))

                    # execute_with_retry(retries, quit_if_title_mismatch, "Test date / time — test times available"
                    #                                                     " - Change booking", "3.70", "3.71", driver)

                    if is_el_found_by_xpath(
                            "Bookable Calendar Btn", "3.72", "//td[@class='BookingCalendar-date--bookable ']", driver):
                        step_three_calendar_btn = execute_with_retry(
                            retries, get_el_by_xpath_else_quit,
                            "Calendar Btn", "3.73", "//td[@class='BookingCalendar-date--bookable ']/div/a", driver)

                        if verify_attribute_href_date_is_earlier(current_test_date, earliest_desired_rebook_date,
                                                                 step_three_calendar_btn, "3.74", driver):
                            logger.debug("3.75a - Found an earlier date in specified parameters!!!")
                            play_song("3.75" + "M", available_booking_sound)

                            # time.sleep(get_random_delay_or_median(form_delay_range_1, form_delay_range_2))
                            execute_with_retry(
                                retries, click_el_else_quit, "Calendar Btn", step_three_calendar_btn, "3.75", driver)
                            # time.sleep(1)  # Wait briefly for radio buttons to load

                            step_three_timeslot_btn = execute_with_retry(
                                retries, get_el_by_xpath_else_quit,
                                "Time Slot Btn", "3.76", "//li[@class='SlotPicker-day is-active']/label", driver)

                            # time.sleep(get_random_delay_or_median(form_delay_range_1, form_delay_range_2))
                            execute_with_retry(
                                retries, click_el_else_quit, "Time Slot Btn", step_three_timeslot_btn, "3.77", driver)

                            step_three_submit_btn = execute_with_retry(
                                retries, get_el_by_attribute_else_quit, "chooseSlotSubmit", "3.78", By.NAME, driver)

                            execute_with_retry(
                                retries, verify_submit_btn_el_else_quit, step_three_submit_btn, "3.79", driver)

                            # time.sleep(get_random_delay_or_median(form_delay_range_1, form_delay_range_2))
                            execute_with_retry(
                                retries, click_el_else_quit, "Submit Btn", step_three_submit_btn, "3.80", driver)

                            on_modal_screen = execute_with_retry(
                                retries, get_el_by_xpath_else_quit, "Modal Window Visible", "3.81",
                                "//div[@class='underlay-wrapper' and @style='display: block;']", driver, 25, 3)

                            # time.sleep(get_random_delay_or_median(form_delay_range_1, form_delay_range_2))
                            step_three_timeslot_modal_btn = execute_with_retry(
                                retries, get_el_by_xpath_else_quit, "Time Continue Btn", "3.82",
                                "//div[@class='underlay-wrapper']/div/section/"
                                "div/div[@class='dialog-wrapper-inner']/div/button", driver)

                            execute_with_retry(retries, click_el_else_quit, "Time Continue Btn",
                                               step_three_timeslot_modal_btn, "3.83", driver)

                            keep_searching_centres = False
                            break
                        else:
                            logger.debug("3.75b - No *earlier* date. URL: " + driver.current_url + " --- Refreshing "
                                                                                                   "the browser...")
                    else:
                        logger.debug("3.73x - No bookable calendar buttons --- Refreshing the browser...")

                    if is_el_found_by_xpath("Search Limit Reached Page", "3.76", "//*[@id='main']/header/h1",
                                            driver) or is_el_found_by_xpath(
                            "Modal Window Visible", "3.77",
                            "//div[@class='underlay' and @style='display: block;']", driver):
                        logger.error(
                            "444" + " - " + "On Search Limit Reached Page/Modal, now quitting when browser dies...")
                        try_screenshot("3.78", "On Search Limit Reached Page/Modal", driver)
                        play_song("999X", captcha_sound_loop, winsound.SND_ASYNC + winsound.SND_LOOP)
                        # Quit the browser instance if browser dies
                        sleep_while_browser_alive("999", driver)
                        logger.debug("Killing process...")
                        kill_thread = True
                        raise Fragile.Break

                    driver.back()
                    time.sleep(get_random_delay_or_median(page_load_delay_range_1, page_load_delay_range_2))
                else:
                    logger.debug("3.63b - Did not find an available booking at " + i + ".")
        if keep_searching_centres:
            logger.debug("3.60x - The current URL is: " + driver.current_url + " --- Refreshing the browser...")
            driver.refresh()
            time.sleep(get_random_delay_or_median(page_load_delay_range_1, page_load_delay_range_2))

    # Step 4 Page - wait for user to do the rest
    set_captcha_codes("4.00", "4.01", "4.02", "4.03")
    time.sleep(get_random_delay_or_median(page_load_delay_range_1, page_load_delay_range_2))

    play_song("4.10M", final_step_loop, winsound.SND_ASYNC + winsound.SND_LOOP)

    while True:
        try:
            logger.debug("4.11a - Waiting on confirm page indefinitely...")
        except Exception as ex:
            log_err(ex, "4.11b", "Error while waiting on confirm page for user indefinitely. Waiting until "
                                 "browser dies...")
            # Quit the browser instance if browser dies
            stop_song("4.12M")
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
