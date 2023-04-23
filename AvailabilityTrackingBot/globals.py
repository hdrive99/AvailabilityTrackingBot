import sys
import json
import os


working_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

if len(sys.argv) == 0:
    config_file_name = "default.json"
else:
    config_file_name = sys.argv[1]

with open(working_dir + "\\configs\\" + config_file_name, "r") as f:
    data = json.load(f)

target_url = data["target_url"]
licence_no = data["licence_no"]
test_date = data["test_date"]
post_code = data["post_code"]
test_centre_names = data["test_centre_names"]
user_title = data["user_title"]
first_names = data["first_names"]
surname = data["surname"]
address_line_1 = data["address_line_1"]
town = data["town"]
post_code_full = data["post_code_full"]
email = data["email"]
contact_number = data["contact_number"]
card_number = data["card_number"]
expiry_month = data["expiry_month"]
expiry_year = data["expiry_year"]
card_holder_name = data["card_holder_name"]
security_code = data["security_code"]
payment_address_same = data["payment_address_same"]
should_wait_on_confirm_page = data["should_wait_on_confirm_page"]
captcha_sound_loop = data["captcha_sound_loop"]
available_booking_sound = data["available_booking_sound"]
final_step_loop = data["final_step_loop"]
error_loop = data["error_loop"]
paused_sound_loop = data["paused_sound_loop"]
waiting_loop = data["waiting_loop"]
form_delay_range_1 = data["form_delay_range_1"]
form_delay_range_2 = data["form_delay_range_2"]
search_delay_range_1 = data["search_delay_range_1"]
search_delay_range_2 = data["search_delay_range_2"]
submit_delay_range_1 = data["submit_delay_range_1"]
submit_delay_range_2 = data["submit_delay_range_2"]
page_load_delay_range_1 = data["page_load_delay_range_1"]
page_load_delay_range_2 = data["page_load_delay_range_2"]
retries = data["retries"]
is_incognito = data["is_incognito"]
should_pause_on_start = data["should_pause_on_start"]
manual_restart = data["manual_restart"]
max_repeat_captcha_checks = data["max_repeat_captcha_checks"]
# Check error-content captcha & repeats this check for "max_repeat_captcha_checks" times, negative for indefinite checks

captcha_code_1, captcha_code_2, captcha_code_3, captcha_code_4 = "1.00", "1.01", "1.02", "1.03"
kill_thread = False
kill_modal_thread = False  # Unused
step_four_btn: any  # Unused
step_four_postcode_form: any  # Unused
step_four_header: any  # Unused
