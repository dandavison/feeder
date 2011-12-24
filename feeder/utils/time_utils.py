from datetime import datetime, timedelta
import time


def get_datetime(struct_time):
    return datetime.fromtimestamp(time.mktime(struct_time))


def as_local_time(datetime):
    return datetime - timedelta(seconds=time.timezone)


def get_datetime_from_time_today(time):
    return (datetime.today() +
            timedelta(hours=time.hour,
                      minutes=time.minute,
                      seconds=time.second))
