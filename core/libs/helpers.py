import random
import string
from datetime import datetime, timezone

TIMESTAMP_WITH_TIMEZONE_FORMAT = '%Y-%m-%dT%H:%M:%S.%f%z'


class GeneralObject:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


def get_utc_now():
    # Return timezone-aware UTC datetime
    return datetime.now(timezone.utc)
