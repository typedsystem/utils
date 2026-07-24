from typed import typed, Str, Bool, Union, Nill
from utils.mods.color import HEX, RGB
from utils.helper.ansi import _apply_styles, _parse_color_to_sgr

class AnsiErr(Exception): pass

class ansi:
    @typed
    def black(
        message: Str,
        bright:    Bool=False,
        italic:    Bool=False,
        bold:      Bool=False,
        underline: Bool=False
    ) -> Str:
        try:
            code = "90" if bright else "30"
            return _apply_styles(
                message,
                color_sgr=code,
                bold=bold,
                italic=italic,
                underline=underline,
            )
        except Exception as e:
            raise AnsiErr(e)

    @typed
    def red(
        message: Str,
        bright:    Bool=False,
        italic:    Bool=False,
        bold:      Bool=False,
        underline: Bool=False
    ) -> Str:
        try:
            code = "91" if bright else "31"
            return _apply_styles(
                message,
                color_sgr=code,
                bold=bold,
                italic=italic,
                underline=underline,
            )
        except Exception as e:
            raise AnsiErr(e)

    @typed
    def green(
        message: Str,
        bright:    Bool=False,
        italic:    Bool=False,
        bold:      Bool=False,
        underline: Bool=False
    ) -> Str:
        try:
            code = "92" if bright else "32"
            return _apply_styles(
                message,
                color_sgr=code,
                bold=bold,
                italic=italic,
                underline=underline,
            )
        except Exception as e:
            raise AnsiErr(e)

    @typed
    def blue(
        message: Str,
        bright:    Bool=False,
        italic:    Bool=False,
        bold:      Bool=False,
        underline: Bool=False
    ) -> Str:
        try:
            code = "94" if bright else "34"
            return _apply_styles(
                message,
                color_sgr=code,
                bold=bold,
                italic=italic,
                underline=underline,
            )
        except Exception as e:
            raise AnsiErr(e)

    @typed
    def yellow(
        message: Str,
        bright:    Bool=False,
        italic:    Bool=False,
        bold:      Bool=False,
        underline: Bool=False
    ) -> Str:
        try:
            code = "93" if bright else "33"
            return _apply_styles(
                message,
                color_sgr=code,
                bold=bold,
                italic=italic,
                underline=underline,
            )
        except Exception as e:
            raise AnsiErr(e)

    @typed
    def magenta(
        message: Str,
        bright:    Bool=False,
        italic:    Bool=False,
        bold:      Bool=False,
        underline: Bool=False
    ) -> Str:
        try:
            code = "95" if bright else "35"
            return _apply_styles(
                message,
                color_sgr=code,
                bold=bold,
                italic=italic,
                underline=underline,
            )
        except Exception as e:
            raise AnsiErr(e)

    @typed
    def cyan(
        message: Str,
        bright:    Bool=False,
        italic:    Bool=False,
        bold:      Bool=False,
        underline: Bool=False
    ) -> Str:
        try:
            code = "96" if bright else "36"
            return _apply_styles(
                message,
                color_sgr=code,
                bold=bold,
                italic=italic,
                underline=underline,
            )
        except Exception as e:
            raise AnsiErr(e)

    @typed
    def white(
        message: Str,
        bright:    Bool=False,
        italic:    Bool=False,
        bold:      Bool=False,
        underline: Bool=False
    ) -> Str:
        try:
            code = "97" if bright else "37"
            return _apply_styles(
                message,
                color_sgr=code,
                bold=bold,
                italic=italic,
                underline=underline,
            )
        except Exception as e:
            raise AnsiErr(e)

    @typed
    def bold(message: Str) -> Str:
        try:
            return _apply_styles(message, bold=True)
        except Exception as e:
            raise AnsiErr(e)

    @typed
    def italic(message: Str) -> Str:
        try:
            return _apply_styles(message, italic=True)
        except Exception as e:
            raise AnsiErr(e)

    @typed
    def underline(message: Str) -> Str:
        try:
            return ansi._apply_styles(message, underline=True)
        except Exception as e:
            raise AnsiErr(e)

    @typed
    def colored(
        message: Str,
        color:     Maybe(Union(Str, HEX, RGB))=None,
        bold:      Bool=False,
        italic:    Bool=False,
        underline: Bool=False
    ) -> Str:
        try:
            color_sgr = _parse_color_to_sgr(color)
            return _apply_styles(
                message,
                color_sgr=color_sgr,
                bold=bold,
                italic=italic,
                underline=underline,
            )
        except Exception as e:
            raise AnsiErr(e)

    @typed
    def print(
        message: Str,
        color:     Maybe(Union(Str, HEX, RGB))=None,
        bold:      Bool=False,
        italic:    Bool=False,
        underline: Bool=False
    ) -> Nill:
        try:
            print(ansi.colored(
                message=message,
                color=color,
                bold=bold,
                italic=italic,
                underline=underline
            ))
        except Exception as e:
            raise AnsiErr(e)
