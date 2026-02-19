# app/utils/timer.py
import time

def get_time():
    return time.time()

def calculate_time(start, end):
    return round(end - start, 2)
