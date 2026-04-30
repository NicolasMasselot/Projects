from datetime import date, datetime, timezone

import pandas as pd


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def to_utc_naive(ts: date | datetime | pd.Timestamp | str) -> datetime:
    timestamp = pd.Timestamp(ts)
    if timestamp.tzinfo is None:
        timestamp = timestamp.tz_localize(timezone.utc)
    else:
        timestamp = timestamp.tz_convert(timezone.utc)
    return timestamp.to_pydatetime().replace(tzinfo=None)


def business_days_between(start: date | datetime | str, end: date | datetime | str) -> int:
    start_date = pd.Timestamp(start).date()
    end_date = pd.Timestamp(end).date()
    return len(pd.bdate_range(start_date, end_date))
