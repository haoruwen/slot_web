import time
import datetime



def safe_print(s):
    try:
        print(s)
    except Exception as e:
        # bypass exception "write could not complete without blocking"
        pass

def print_info(text):
    safe_print(time.strftime('[%Y-%m-%d %H:%M:%S] ') + text)


def time_to_string(a_time):
    return datetime.datetime.strftime(a_time, '%Y-%m-%d %H:%M:%S')
