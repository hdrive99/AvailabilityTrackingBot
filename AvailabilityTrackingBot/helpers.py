from globals import *
import os
import psutil
import random


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


def restart_program(logging):
    """Restarts the current program, with file objects and descriptors cleanup"""

    try:
        p = psutil.Process(os.getpid())
        for handler in p.get_open_files() + p.connections():
            os.close(handler.fd)
    except Exception as exc:
        logging.error(exc)

    python = sys.executable
    os.execl(python, python, *sys.argv)


def namer(name):
    return name.replace(".log", "") + ".log"


def set_captcha_codes(code1, code2, code3, code4):
    global captcha_code_1, captcha_code_2, captcha_code_3, captcha_code_4
    captcha_code_1 = code1
    captcha_code_2 = code2
    captcha_code_3 = code3
    captcha_code_4 = code4

def get_random_delay_or_median(time_range_1, time_range_2):
    if type(time_range_1) == int and type(time_range_2) == int:
        return random.randint(time_range_1, time_range_2)
    else:
        return (time_range_1 + time_range_2) / 2
