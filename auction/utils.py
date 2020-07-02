import time

# Convert datetime to integer (epoch time)
def to_epoch(value):
    return int(time.mktime(value.timetuple()))

# Convert integer (epoch time) to a datetime
def from_epoch(value):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(value))
