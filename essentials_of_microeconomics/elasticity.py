from dataclasses import dataclass
from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd
from shiny import module, reactive, render, req, ui
from sympy import (
    Eq,
    S,
    Symbol,
    diff,
    evaluate,
    latex,
    parse_expr,
    plot,
    solve,
    symbols,
    zoo,
)

symbol_epsilon: Symbol = symbols("varepsilon")


@dataclass(frozen=True)
class ApplicationInfo:
    name: str
    definition: str
    symbol_epsilon: Symbol = symbol_epsilon
    symbol_x: Symbol = symbols("x", positive=True)
    symbol_y: Symbol = symbols("y", positive=True)
    equation: str = ""
    value_x: str = ""
    interpret: Optional[pd.DataFrame] = None


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
    "10",
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
    "10",
    pd.DataFrame(
        [[Eq(symbol_epsilon, 0), "perfecly inelastic", "not at all"],
         [(S(0) < symbol_epsilon) & (symbol_epsilon < S(-1)), "inelastic", "not very"],
         [Eq(symbol_epsilon, 1), "unit elastic", "fairly"],
         [symbol_epsilon > S(0), "elastic", "very"],
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
    "10",
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
    "10",
    pd.DataFrame(
        [[symbol_epsilon < S(0), "inferior", "instant noodles and frozen food"],
         [Eq(symbol_epsilon, 0), "independent", ""],
         [(S(0) < symbol_epsilon) & (symbol_epsilon <= S(1)), "independent", "food and clothes in general"],
         [symbol_epsilon > S(1), "substitutes", "jewelry and high-end watches"]],
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
                ui.input_text("point_x",
                              fr"Enter a value for \({latex(I.symbol_x)}\):",
                              I.value_x),
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
def application_server(input, output, session, I: ApplicationInfo):

    @reactive.Calc
    def y():
        relation = parse_expr(
            input.equation(),
            {I.symbol_x.name: I.symbol_x, I.symbol_y.name: I.symbol_y},
            transformations="all")
        solutions = solve(relation, I.symbol_y)
        req(len(solutions) == 1)
        return solutions[0]

    @reactive.Calc
    def epsilon():
        return diff(y(), I.symbol_x) * S(I.symbol_x) / I.symbol_y

    @reactive.Calc
    def point_x():
        try:
            return parse_expr(input.point_x(), transformations="all")
        except:
            return None

    @reactive.Calc
    def point_y():
        req(point_x() is not None, y())
        return y().subs({I.symbol_x: point_x()})

    @reactive.Calc
    def point_epsilon():
        return epsilon().subs({I.symbol_x: point_x(), I.symbol_y: point_y()})

    @output
    @render.text
    def equation():
        return "$$" + latex(I.symbol_y) + "=" + latex(y()) + "$$"

    @output
    @render.text
    def elasticity():
        epsilon_alt = epsilon().subs({I.symbol_y: y()})
        return (
            "Using the point method to elasticity,"
            + "$$"
            + latex(I.symbol_epsilon)
            + r"= \frac{d" + latex(I.symbol_y) + "}{d" + latex(I.symbol_x) + "}"
            + r"\cdot"
            + r"\frac{" + latex(I.symbol_x) + "}{" + latex(I.symbol_y) + "}"
            + "=" + latex(epsilon())
            + ("=" + latex(epsilon_alt) if epsilon_alt != epsilon() else "")
            + "$$")

    @output
    @render.text
    def point():
        req(point_x(), point_y())
        return ("$$(" + latex(I.symbol_x) + "," + latex(I.symbol_y) + ")"
                + "= (" + latex(point_x()) + "," + latex(point_y()) + ")$$")

    @output
    @render.text
    def point_elasticity():
        return (
            r"Substituting the point into \(" + latex(I.symbol_epsilon) + r"\),"
            + "$$"
            + latex(I.symbol_epsilon) + "=" + latex(point_epsilon())
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
        ax = plt.subplot()
        p, = plot(y(), show=False)
        ax.plot(*p.get_points()[::-1])
        ax.set_xlim(0)
        ax.set_ylim(0)
        ax.set_xlabel(f"${latex(I.symbol_y)}$")
        ax.set_ylabel(f"${latex(I.symbol_x)}$")
        return ax


@module.server
def elasticity_server(input, output, session):
    application_server("demand", demand_info)
    application_server("supply", supply_info)
    application_server("cross_price", cross_price_info)
    application_server("income", income_info)
