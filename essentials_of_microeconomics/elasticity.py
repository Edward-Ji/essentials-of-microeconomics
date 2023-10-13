from dataclasses import dataclass

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from shiny import module, reactive, render, req, ui
from sympy import (
    Eq,
    S,
    Symbol,
    diff,
    evaluate,
    latex,
    plot,
    simplify,
    solve,
    symbols,
    zoo,
)

from util import latex_approx, parse_expr_safer

symbol_epsilon: Symbol = symbols("varepsilon")


@dataclass(frozen=True)
class ApplicationInfo:
    name: str
    definition: str
    symbol_epsilon: Symbol
    symbol_x: Symbol
    symbol_y: Symbol
    equation: str
    value: str
    interpret: pd.DataFrame


demand_info = ApplicationInfo(
    "Elasticity of demand",
    r"""
    The elasticity of demand (\(\varepsilon_d\)) measures how sensitive the
    quantity \(Q_d\) demanded of a good change in its price \(P\).
    """,
    symbols("varepsilon_d"),
    symbols("P", positive=True),
    symbols("Q_d", positive=True),
    "Q_d = 100 - P",
    "Q_d = 90",
    pd.DataFrame(
        [[Eq(symbol_epsilon, zoo, evaluate=False), "perfecly elastic", "extremely"],
         [symbol_epsilon < S(-1), "elastic", "very"],
         [Eq(symbol_epsilon, -1), "unit elastic", "fairly"],
         [(S(-1) < symbol_epsilon) & (symbol_epsilon < S(0)), "inelastic", "not very"],
         [Eq(symbol_epsilon, 0), "perfecly inelastic", "not at all"]],
        columns=["Elasticity of demand", "How elastic", "Responsiveness"])
)

supply_info = ApplicationInfo(
    "Elasticity of supply",
    r"""
    The elasticity of supply (\(\varepsilon_s\)) measures how sensitive the
    quantity \(Q_s\) supplied of a good change in its price \(P\).
    """,
    symbols("varepsilon_s"),
    symbols("P", positive=True),
    symbols("Q_s", positive=True),
    "Q_s = P - 5",
    "P = 10",
    pd.DataFrame(
        [[Eq(symbol_epsilon, 0), "perfecly inelastic", "not at all"],
         [(S(0) < symbol_epsilon) & (symbol_epsilon < S(1)), "inelastic", "not very"],
         [Eq(symbol_epsilon, 1), "unit elastic", "fairly"],
         [symbol_epsilon > S(1), "elastic", "very"],
         [Eq(symbol_epsilon, zoo, evaluate=False), "perfecly elastic", "extremely"]],
        columns=["Elasticity of supply", "How elastic", "Responsiveness"])
)

cross_price_info = ApplicationInfo(
    "Cross-price elasticity",
    r"""
    The cross-price elasticity examines the relationship between the quantity
    demanded of one good and the price of another related good. Specifically, it
    measures how sensitive the quantity \(Q_A\) demanded of a good A changes in
    the price \(P_B\) of another good B.
    """,
    symbols("varepsilon_AB"),
    symbols("P_B", positive=True),
    symbols("Q_A", positive=True),
    "Q_A = 10",
    "P_B = 1",
    pd.DataFrame(
        [[symbol_epsilon < S(0), "complements", "bacon and eggs"],
         [Eq(symbol_epsilon, 0), "independent", "ice cream and chainsaws"],
         [symbol_epsilon > S(0), "substitutes", "tea and coffee"]],
        columns=["Cross-price elasticity", "Relationship", "Example"])
)

income_info = ApplicationInfo(
    "Income elasticity",
    r"""
    Income elasticity \(\eta\) measures how sensitive the quantity demanded of a
    good \(Q\) changes in income \(Y\).
    """,
    symbols("eta"),
    symbols("Y", positive=True),
    symbols("Q", positive=True),
    "Q = Y",
    "Y = 10",
    pd.DataFrame(
        [[symbol_epsilon < S(0), "inferior", "instant noodles and frozen food"],
         [Eq(symbol_epsilon, 0), "neutral", ""],
         [(S(0) < symbol_epsilon) & (symbol_epsilon <= S(1)), "normal", "food and clothes in general"],
         [symbol_epsilon > S(1), "luxury", "jewelry and high-end watches"]],
        columns=["Income elasticity", "Type of good", "Example"])
)


@module.ui
def application_ui(I: ApplicationInfo):
    return ui.nav(
        I.name,
        ui.p(I.definition),
        ui.row(
            ui.column(
                6,
                ui.input_text("equation",
                              fr"""Enter an equation for \({latex(I.symbol_x)}\)
                              and \({latex(I.symbol_y)}\):""",
                              I.equation),
            ),
            ui.column(6, ui.output_text("equation"))
        ),
        ui.output_text("elasticity"),
        ui.row(
            ui.column(
                6,
                ui.input_text("point",
                              fr"""Enter a value for \({latex(I.symbol_x)}\)
                              or \({latex(I.symbol_y)}\):""",
                              I.value),
            ),
            ui.column(6, ui.output_text("point"))
        ),
        ui.output_text("point_elasticity"),
        ui.output_table("interpret"),
        ui.output_plot("curve")
    )


@module.ui
def elasticity_ui():
    return ui.nav(
        "Elasticity",
        ui.h1("Elasticity"),
        ui.p("""We are interested in measuring how a change in one variable
             affects another. One issue with measuring quantitative changes is
             that different markets use different units of measurement. A way we
             deal with this is to look at proportional changes."""),
        ui.h2("Measuring elasticity"),
        ui.p(r"""Elasticity \(\varepsilon\) measures how responsive one variable
             \(y\) changes in another variable \(x\); We can calculate it by
             deciding the percentage change in \(y\) by the percentage change in
             \(x\):"""),
        ui.p(r"$$\varepsilon=\frac{\%\Delta y}{\%\Delta x}$$"),
        ui.p(r"""where \(\%\Delta x=\frac{\Delta x}{x}\). The larger the
             absolute value of \(\varepsilon\), the more responsive \(y\) is to
             changes in \(x\); Conversely, the smaller the absolute value of
             \(\varepsilon\), the less responsive \(y\) is to changes in
             \(x\)."""),
        ui.h3("Point method"),
        ui.p(r"""If we are interested in elasticity at a particular point and
             \(y(x)\) is differentiable at that point, we can use the point
             method."""),
        ui.p(r"$$\varepsilon = \frac{\Delta y / {y}}{\Delta x / {x}}"
             r"= \frac{\Delta y}{\Delta x} \cdot \frac x y"
             r"= \frac{dy}{dx} \cdot \frac x y$$"),
        ui.h3("Midpoint (or arc) method"),
        ui.p("""If we are interested in elasticity when moving from one point to
             another, we use the midpoint method."""),
        ui.p(r"$$\varepsilon = \frac{\Delta y / {y^m}}{\Delta x / {x^m}}"
             r"= \frac{\Delta y}{\Delta x} \cdot \frac{x^m}{y^m}$$"),
        ui.p(r"where \(x^m=\frac{x_1+x_2}2\) and \(y^m=\frac{y_1+y_2}2\)."),
        ui.h2("Applications"),
        ui.navset_pill(
            application_ui("demand", demand_info),
            application_ui("supply", supply_info),
            application_ui("cross_price", cross_price_info),
            application_ui("income", income_info)
        )
    )


@module.server
def application_server(input, output, session, I: ApplicationInfo, settings):

    @reactive.Calc
    def y():
        relation = parse_expr_safer(
            input.equation(),
            {I.symbol_x.name: I.symbol_x, I.symbol_y.name: I.symbol_y},
            transformations="all")
        solutions = solve(relation, I.symbol_y, dict=True)
        req(len(solutions) == 1)
        return solutions[0][I.symbol_y]

    @reactive.Calc
    def epsilon():
        return diff(y(), I.symbol_x) * S(I.symbol_x) / I.symbol_y

    @reactive.Calc
    def epsilon_x():
        return simplify(epsilon().subs({I.symbol_y: y()}))

    @reactive.Calc
    def point_xy():
        try:
            eq = parse_expr_safer(
                input.point(),
                {I.symbol_x.name: I.symbol_x, I.symbol_y.name: I.symbol_y},
                transformations="all")
            solutions = solve(
                [eq, Eq(I.symbol_y, y())], (I.symbol_x, I.symbol_y), dict=True)
            return solutions[0]
        except:
            return {}

    @reactive.Calc
    def point_x():
        req(point_xy())
        return point_xy()[I.symbol_x]

    @reactive.Calc
    def point_y():
        req(point_xy())
        return point_xy()[I.symbol_y]

    @reactive.Calc
    def point_epsilon():
        return simplify(
            epsilon().subs({I.symbol_x: point_x(), I.symbol_y: point_y()}))

    @output
    @render.text
    def equation():
        return (
            "$$"
            + latex(I.symbol_y) + "="
            + latex_approx(y(), settings.perc(), settings.approx())
            + "$$")

    @output
    @render.text
    def elasticity():
        return (
            "Using the point method to elasticity,"
            + "$$"
            + latex(I.symbol_epsilon)
            + r"= \frac{d" + latex(I.symbol_y) + "}{d" + latex(I.symbol_x) + "}"
            + r"\cdot"
            + r"\frac{" + latex(I.symbol_x) + "}{" + latex(I.symbol_y) + "}"
            + "=" + latex(epsilon())
            + ("=" + latex(epsilon_x()) if epsilon_x() != epsilon() else "")
            + "$$")

    @output
    @render.text
    def point():
        return (
            r"$$\begin{align*}"
            + latex(I.symbol_x) + "&="
            + latex_approx(point_x(), settings.perc(), settings.approx())
            + r"\\"
            + latex(I.symbol_y) + "&="
            + latex_approx(point_y(), settings.perc(), settings.approx())
            + r"\end{align*}$$")

    @output
    @render.text
    def point_elasticity():
        return (
            r"Substituting the point into \(" + latex(I.symbol_epsilon) + r"\),"
            + "$$"
            + latex(I.symbol_epsilon) + "="
            + latex_approx(point_epsilon(), settings.perc(), settings.approx())
            + "$$")

    @output
    @render.table
    def interpret():
        def highlight_true(row):
            if point_x() is not None:
                try:
                    if row[0].subs({symbol_epsilon: point_epsilon()}):
                        return ["background-color: lightgreen"] * len(row)
                except TypeError:
                    pass
            return [None] * len(row)

        def format_cell(cell):
            if isinstance(cell, str):
                return cell
            else:
                with evaluate(False):
                    cell = latex(cell.subs({symbol_epsilon: I.symbol_epsilon}))
                return r"\(" + cell + r"\)"

        return (I.interpret.style
            .set_table_attributes('class="dataframe table shiny-table w-auto"')
            .apply(highlight_true, axis=1)
            .format(format_cell)
            .hide(axis="index"))

    @output
    @render.plot
    def curve():
        nb = 50
        ax = plt.subplot()
        xx, yy = plot(
            y(), (I.symbol_x, 0, 100),
            show=False, adaptive=False, nb_of_points=nb)[0].get_points()
        _, cc = plot(
            epsilon_x(), (I.symbol_x, 0, 100),
            show=False, adaptive=False, nb_of_points=nb)[0].get_points()
        sc = plt.scatter(np.resize(yy, nb), xx, c=np.resize(cc, nb),
                         norm=mpl.colors.AsinhNorm())
        ax.set_xlim(0)
        ax.set_ylim(0)
        ax.set_xlabel(f"${latex(I.symbol_y)}$")
        ax.set_ylabel(f"${latex(I.symbol_x)}$")
        ax.get_figure().colorbar(sc, label=f"${latex(I.symbol_epsilon)}$")
        return ax


@module.server
def elasticity_server(input, output, session, settings):
    application_server("demand", demand_info, settings)
    application_server("supply", supply_info, settings)
    application_server("cross_price", cross_price_info, settings)
    application_server("income", income_info, settings)
