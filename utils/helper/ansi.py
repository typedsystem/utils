import re
from typed import Str, Maybe, Bool, Union
from utils.mods.color import HEX, RGB

_ANSI_WRAPPER_RE = re.compile(r'^\033\[([0-9;]+)m(.*?)\033\[0m$', re.DOTALL)

_COLOR_CODES = {
    "black": 30,
    "red": 31,
    "green": 32,
    "yellow": 33,
    "blue": 34,
    "magenta": 35,
    "cyan": 36,
    "white": 37,
    "bright_black": 90,
    "bright_red": 91,
    "bright_green": 92,
    "bright_yellow": 93,
    "bright_blue": 94,
    "bright_magenta": 95,
    "bright_cyan": 96,
    "bright_white": 97,
}

def _parse_wrapped(text: Str):
    m = _ANSI_WRAPPER_RE.match(text)
    if not m:
        return [], text
    codes = m.group(1).split(";")
    inner = m.group(2)
    return codes, inner

def _apply_styles(
    message: Str,
    *,
    color_sgr: Maybe(Str)=None,
    bold: Bool=False,
    italic: Bool=False,
    underline: Bool=False,
) -> Str:
    existing_codes, inner = _parse_wrapped(message)

    new_codes = existing_codes.copy()

    if bold:
        new_codes.append("1")
    if italic:
        new_codes.append("3")
    if underline:
        new_codes.append("4")
    if color_sgr is not None:
        new_codes.append(color_sgr)

    if not new_codes:
        return inner

    seen = set()
    deduped = []
    for c in new_codes:
        if c not in seen:
            seen.add(c)
            deduped.append(c)

    return f"\033[{';'.join(deduped)}m{inner}\033[0m"

def _parse_color_to_sgr(color: Union(Str, HEX, RGB)) -> Str:
    if color is None:
        return None

    if color in Str and not color in HEX:
        code = _COLOR_CODES.get(color.lower())
        if code is not None:
            return str(code)

    if color in HEX:
        try:
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            return f"38;2;{r};{g};{b}"
        except ValueError:
            return None

    if color in RGB:
        try:
            r, g, b = (int(color[0]), int(color[1]), int(color[2]))
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            return f"38;2;{r};{g};{b}"
        except (TypeError, ValueError):
            return None

    return None
