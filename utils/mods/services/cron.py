from datetime import datetime, timedelta
from typed import typed, model, Set, Regex, Str, Union, Int, Float
from utils.mods.number import Nat
from utils.mods.helper.cron import _CRON_REGEX, _parse_cron_field

Cron = Regex(_CRON_REGEX)

@model
class CronModel:
    minutes: Set(Nat)
    hours: Set(Nat)
    days_of_month: Set(Nat)
    months: Set(Nat)
    days_of_week: Set(Nat)

class CronErr(Exception): pass

class cron:
    @typed
    def parse(cron: Cron) -> CronModel:
        fields = cron.split()
        if len(fields) != 5:
            raise ValueError(f"Invalid cron expression (need 5 fields): {cron!r}")

        minute_f, hour_f, dom_f, month_f, dow_f = fields

        minutes = _parse_cron_field(minute_f, 0, 59)
        hours = _parse_cron_field(hour_f, 0, 23)
        days_of_month = _parse_cron_field(dom_f, 1, 31)
        months = _parse_cron_field(month_f, 1, 12)

        dows_raw = _parse_cron_field(dow_f, 0, 7)
        days_of_week = set()
        for d in dows_raw:
            if d == 7:
                d = 0
            days_of_week.add(d)

        return CronModel(
            minutes=minutes,
            hours=hours,
            days_of_month=days_of_month,
            months=months,
            days_of_week=days_of_week
        )

    @typed
    def next_run(expr: Str, last_run: Union(Str, Int, Float)=datetime.now()) -> datetime:
        if last_run in Str:
            last_run = datetime.fromisoformat(last_run)
        if last_run in Int or last_run in Float:
            last_run = datetime.fromtimestamp(last_run)

        cron_model = cron.parse(expr)

        current = (last_run.replace(second=0, microsecond=0) + timedelta(minutes=1))

        end = current + timedelta(days=366)

        while current < end:
            minute = current.minute
            hour = current.hour
            dom = current.day
            month = current.month
            dow = current.weekday()

            if (
                minute in cron_model.minutes
                and hour in cron_model.hours
                and month in cron_model.months
            ):
                dom_any = len(cron_model.days_of_month) == 31
                dow_any = len(cron_model.days_of_week) == 7

                dom_match = dom in cron_model.days_of_month
                dow_match = dow in cron_model.days_of_week

                if dom_any and dow_any:
                    return current
                elif dom_any and dow_match:
                    return current
                elif dow_any and dom_match:
                    return current
                elif dom_match or dow_match:
                    return current

            current += timedelta(minutes=1)

        raise RuntimeError(f"Could not find next run time for cron expression {expr!r}")
