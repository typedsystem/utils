from functools import lru_cache as cache
from typed import typed, Str, Maybe, Regex, name
from typed.meta import STR
from datetime import datetime as _datetime
from zoneinfo import ZoneInfo
from utils.mods.helper.datetime import (
    _ALLOWED_CHARS,
    _DATE_DIRECTIVES,
    _TIME_DIRECTIVES,
    _DATETIME_DIRECTIVES
)

DatetimeFormat = Regex(f"^{_ALLOWED_CHARS}({_DATETIME_DIRECTIVES}{_ALLOWED_CHARS})+$")
DateFormat = Regex(f"^{_ALLOWED_CHARS}({_DATE_DIRECTIVES}{_ALLOWED_CHARS})+$")
TimeFormat = Regex(f"^{_ALLOWED_CHARS}({_TIME_DIRECTIVES}{_ALLOWED_CHARS})+$")

class TIMEZONE(STR):
    def __instancecheck__(cls, instance):
        if not instance in Str:
            return False
        try:
            ZoneInfo(instance)
            return True
        except:
            return False

TimeZone = TIMEZONE("TimeZone", (Str,), {"__display__": "TimeZone", "__null__": ""})

@cache
def Date(date_format):
    from typed.mods.types.base import TYPE, Str
    if not isinstance(date_format, DateFormat):
        raise TypeError(
            "Date is not in valid format:"
            f" ==> '{date_format}' is not a valid date format string."
            f"      [expected_type] {name(DateFormat)}"
            f"      [received type] {name(TYPE(date_format))}"
        )
    class DATE(TYPE(Str)):
        _date_format_str = date_format
        def __instancecheck__(cls, instance):
            if not isinstance(instance, Str):
                return False
            try:
                datetime.strptime(instance, cls._date_format_str).date()
                return True
            except ValueError:
                return False
        def __repr__(self):
            return f"Date('{self._date_format_str}')"
    class_name = f"Date({date_format})"
    return DATE(class_name, (Str,), {
        "__display__": class_name,
        "__null__": "",
    })

@cache
def Time(time_format):
    from typed.mods.types.base import TYPE, Str
    if not isinstance(time_format, TimeFormat):
        raise TypeError(
            "Time is not in valid format:"
            f" ==> '{time_format}' is not a valid time format string."
            f"      [expected_type] {name(TimeFormat)}"
            f"      [received type] {name(TYPE(time_format))}"
        )

    class TIME(TYPE(Str)):
        _time_format_str = time_format
        def __instancecheck__(cls, instance):
            if not isinstance(instance, Str):
                return False
            try:
                datetime.strptime(instance, cls._time_format_str).time()
                return True
            except ValueError:
                return False

        def __repr__(self):
            return f"Time('{self._time_format_str}')"

    class_name = f"Time({time_format})"
    return TIME(class_name, (Str,), {
        "__display__": class_name,
        "__null__": "",
    })

@cache
def Datetime(datetime_format):
    from typed.mods.types.base import TYPE, Str
    if not isinstance(datetime_format, DatetimeFormat):
        raise TypeError(
            "Datetime is not in valid format:"
            f" ==> '{datetime_format}' is not a valid datetime format string."
            f"      [expected_type] {name(DatetimeFormat)}"
            f"      [received type] {name(TYPE(datetime_format))}"
        )

    class DATETIME(TYPE(Str)):
        _datetime_format_str = datetime_format

        def __instancecheck__(cls, instance):
            if not isinstance(instance, str):
                return False
            try:
                datetime.datetime.strptime(instance, cls._datetime_format_str)
                return True
            except ValueError:
                return False

        def __repr__(self):
            return f"Datetime('{self._datetime_format_str}')"

    class_name = f"Datetime({datetime_format})"
    return DATETIME(class_name, (Str,), {
        "__display__": class_name,
        "__null__": "",
    })

class DatetimeErr(Exception): pass

class datetime:
    @typed
    def now(tz: Maybe(TimeZone)=None, format: Maybe(DatetimeFormat)=None) -> Str:
        try:
            if tz:
                if format:
                    return _datetime.now(ZoneInfo(tz)).strftime(format)
                return _datetime.now(ZoneInfo(tz)).isoformat()
            if format:
                return _datetime.now().strftime(format)
            return _datetime.now().isoformat()
        except Exception as e:
            raise DatetimeErr(e)

    class date:
        @typed
        def now(tz: Maybe(TimeZone)=None, format: DateFormat='%Y-%m-%d') -> Str:
            try:
                if tz:
                    if format:
                        return _datetime.now(ZoneInfo(tz)).strftime(format)
                    return _datetime.now(ZoneInfo(tz)).isoformat()
                if format:
                    return _datetime.now().strftime(format)
                return _datetime.now().isoformat()
            except Exception as e:
                raise DatetimeErr(e)

    class time:
        @typed
        def now(tz: Maybe(TimeZone)=None, format: TimeFormat='%H:%m:%s') -> Str:
            try:
                if tz:
                    if format:
                        return _datetime.now(ZoneInfo(tz)).strftime(format)
                    return _datetime.now(ZoneInfo(tz)).isoformat()
                if format:
                    return _datetime.now().strftime(format)
                return _datetime.now().isoformat()
            except Exception as e:
                raise DatetimeErr(e)
