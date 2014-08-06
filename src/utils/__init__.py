#!/usr/bin/env python
# -*- coding: utf-8 -*-
from calendar import monthrange
from datetime import timedelta, date

from django.utils import timezone


def unix_time(localtime):
    return int(localtime.strftime("%s"))


def unix_time_utc(utc_time):
    # convert a utc datetime to unix second
    return int(timezone.localtime(utc_time).strftime("%s"))


def unix_time_utc_day(utc_day):
    # convert a utc date to unix second
    return int(utc_day.strftime("%s"))


def unix_time_millis_utc(utc_time):
    return unix_time_utc(utc_time) * 1000.0


def unix_time_millis(localtime):
    return unix_time(localtime) * 1000.0


def unix_time_millis_utc_day(utc_day):
    return unix_time_utc_day(utc_day) * 1000.0


def utc_time_to_text(utc_time):
    # it make no sense to be precise to seconds
    return timezone.localtime(utc_time).strftime("%Y-%m-%d %H:%M") if utc_time else ""


def local_time_to_text(local_time):
    # it make no sense to be precise to seconds
    return local_time.strftime("%Y-%m-%d %H:%M") if local_time else ""


def get_begin_day_of_month(dt):
    return dt.replace(day=1)


def get_end_day_of_month(dt):
    mdays = monthrange(dt.year, dt.month)[1]
    return dt.replace(day=mdays)


def get_begin_day_of_month1(year, month):
    return date(year=year, month=month, day=1)


def get_end_time_of_day(dt):
    return dt.replace(hour=23, minute=59, second=59)


def get_end_day_of_month1(year, month):
    return date(year=year, month=month, day=monthrange(year, month)[1])


def get_month_delta(d1, d2):
    delta = 0
    d1_begin = get_begin_day_of_month(d1)
    d2_begin = get_begin_day_of_month(d2)
    while True:
        mdays = monthrange(d1_begin.year, d1_begin.month)[1]
        d1_begin += timedelta(days=mdays)
        if d1_begin <= d2_begin:
            delta += 1
        else:
            break
    return delta


def add_months(source_date, months):
    month = source_date.month - 1 + months
    year = source_date.year + month / 12
    month = month % 12 + 1
    day = min(source_date.day, monthrange(year, month)[1])
    return date(year, month, day)


def range_date_for_day(start_date, end_date, right_closed=True):
    delta = (end_date - start_date).days + (2 if right_closed else 1)
    for n in range(int(delta)):
        yield start_date + timedelta(days=n)


def range_date_for_month(start_date, end_date):
    delta = get_month_delta(start_date, end_date) + 1
    last_day_of_month = get_end_day_of_month(start_date)
    for n in range(delta):
        # last_day_of_month = add_months(last_day_of_month, 1)
        yield add_months(last_day_of_month, n)


def prepend_item_to_tuple(item, dest_tuple):
    dest_tuple_list = list(dest_tuple)
    dest_tuple_list.insert(0, item)
    return tuple(dest_tuple_list)


def zero_int(number):
    return int(number) if number else 0

