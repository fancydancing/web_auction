import time


def to_epoch(value):
    """Convert datetime to integer (epoch time)"""
    return int(time.mktime(value.timetuple()))


def from_epoch(value:int):
    """Convert integer (epoch time) to a datetime"""
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(value))
