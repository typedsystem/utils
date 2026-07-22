def _parse_cron_field(field, min_value, max_value):
    """
    Parse a single cron field (like '*/5', '1,2,3', '1-10/2', '*') into a set of ints.
    """
    values = set()

    if field == '*':
        return set(range(min_value, max_value + 1))

    parts = field.split(',')
    for part in parts:
        part = part.strip()
        if not part:
            continue

        if '/' in part:
            base, step_str = part.split('/', 1)
            step = int(step_str)
            if base == '*':
                start, end = min_value, max_value
            elif '-' in base:
                start_str, end_str = base.split('-', 1)
                start = int(start_str)
                end = int(end_str)
            else:
                start = int(base)
                end = int(base)

            for v in range(start, end + 1, step):
                if min_value <= v <= max_value:
                    values.add(v)
            continue

        if '-' in part:
            start_str, end_str = part.split('-', 1)
            start = int(start_str)
            end = int(end_str)
            for v in range(start, end + 1):
                if min_value <= v <= max_value:
                    values.add(v)
            continue

        v = int(part)
        if min_value <= v <= max_value:
            values.add(v)
    return values

_STEP = r'(?:/[1-9][0-9]*)?'

_MIN_ITEM = rf'(?:\*(?:{_STEP})|(?:[0-5]?\d)(?:-(?:[0-5]?\d))?(?:{_STEP}))'
_HOUR_ITEM = rf'(?:\*(?:{_STEP})|(?:[01]?\d|2[0-3])(?:-(?:[01]?\d|2[0-3]))?(?:{_STEP}))'
_DOM_ITEM = rf'(?:\*(?:{_STEP})|(?:0?[1-9]|[12]\d|3[01])(?:-(?:0?[1-9]|[12]\d|3[01]))?(?:{_STEP}))'
_MON_NAMES = r'(?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)'
_MON_ITEM = rf'(?:\*(?:{_STEP})|(?:0?[1-9]|1[0-2]|{_MON_NAMES})(?:-(?:0?[1-9]|1[0-2]|{_MON_NAMES}))?(?:{_STEP}))'
_DOW_NAMES = r'(?:SUN|MON|TUE|WED|THU|FRI|SAT)'
_DOW_ITEM = rf'(?:\*(?:{_STEP})|(?:[0-7]|{_DOW_NAMES})(?:-(?:[0-7]|{_DOW_NAMES}))?(?:{_STEP}))'

_CRON_REGEX = rf'^\s*{_MIN_ITEM}\s+{_HOUR_ITEM}\s+{_DOM_ITEM}\s+{_MON_ITEM}\s+{_DOW_ITEM}\s*$'
