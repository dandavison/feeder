from datetime import datetime, timedelta
import time


def get_datetime(struct_time):
    return datetime.fromtimestamp(time.mktime(struct_time))


def as_local_time(datetime):
    return datetime - timedelta(seconds=time.timezone)


