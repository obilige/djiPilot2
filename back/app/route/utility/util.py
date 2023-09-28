import threading
from datetime import datetime


def set_interval(func, sec, *param):
    def func_wrapper():
        set_interval(func, sec, *param)
        func(*param)
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t