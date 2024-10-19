from enum import Enum
from functools import wraps

from pandas.io.formats.style import plt
from shiny import render
from sympy import N, latex, parse_expr


class Approx(Enum):
    HIDE = "Hide"
    REPLACE = "Replace"
    APPEND = "Append"


def latex_approx(expr, perc: int = 15, approx: Approx = Approx.HIDE):
    if approx == Approx.HIDE:
        return latex(expr)
    evalf = N(expr, perc)
    if evalf == expr:
        return latex(expr)
    if approx == Approx.REPLACE:
        return latex(evalf)
    if approx == Approx.APPEND:
        return latex(expr) + r"\approx " + latex(evalf)
    assert False


sympy_dict = {}
exec("from sympy import *", sympy_dict)  # pylint: disable=exec-used


def parse_expr_safer(*args, **kwargs):
    kwargs.setdefault("global_dict", {}).update(sympy_dict)
    return parse_expr(*args, **kwargs)


def styled_plot(settings):
    def decorator(func):
        @render.plot(height=400, transparent=True)
        @wraps(func)
        def wrapper():
            with plt.style.context(settings.style()):
                return func()
        return wrapper
    return decorator
