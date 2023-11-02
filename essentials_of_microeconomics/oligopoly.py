from itertools import zip_longest
from typing import TYPE_CHECKING

import pandas as pd
from shiny import module, reactive, render, ui

from util import latex_approx, parse_expr_safer

if TYPE_CHECKING:
    from pandas.io.formats.style import Styler


price_war_df = pd.DataFrame(
    [[(4, 4), (1, 5)], [(5, 1), (3, 3)]],
    columns=["High", "Low"],
    index=["High", "Low"])


def style_tuple_df(df) -> "Styler":
    def classes_tuple(cell):
        if isinstance(cell, tuple):
            return "tuple"
        return ""

    def format_tuple(cell):
        if isinstance(cell, tuple):
            x, y = cell
            return (fr"<div class='right'> \({y}\)</div>"
                    fr"<div class='left'>\({x}\) </div>")

    return (
        df.style
        .set_table_attributes("class='table table-bordered w-auto'")
        .set_td_classes(df.map(classes_tuple))
        .format(format_tuple)
    )


@module.ui
def payoff_ui(df, max_size=5):
    n_row, n_col = df.shape

    columns = [ui.div(class_="col-2")]
    for i, column in zip_longest(range(max_size), df.columns):
        columns.append(ui.panel_conditional(
            f"input.n_col > {i}",
            ui.input_text(f"column_{i}", "", column),
            class_="col-4"))
    header_row = ui.row(*columns, class_="flex-nowrap")

    rows = []
    for i, index in zip_longest(range(max_size), df.index):
        row = [ui.div(ui.input_text(f"row_{i}", "", index), class_="col-2")]
        for j, column in zip_longest(range(max_size), df.columns):
            if index is not None and column is not None:
                x, y = df.loc[index, column]
            else:
                x, y = "", ""
            row.append(ui.panel_conditional(
                f"input.n_col > {j}",
                ui.input_text(f"cell_{i}{j}1", "", str(x)),
                class_="col-2"))
            row.append(ui.panel_conditional(
                f"input.n_col > {j}",
                ui.input_text(f"cell_{i}{j}2", "", str(y)),
                class_="col-2"))
        rows.append(ui.panel_conditional(
            f"input.n_row > {i}", ui.row(*row, class_="flex-nowrap")))

    return ui.div(
        ui.row(
            ui.div(
                ui.input_numeric(
                    "n_row", "", min=2, max=max_size, value=n_row),
                class_="col-2"),
            ui.div(r"\(\times\)", class_="col-1 text-center"),
            ui.div(
                ui.input_numeric(
                    "n_col", "", min=2, max=max_size, value=n_col),
                class_="col-2"),
            ui.div(
                ui.input_action_button(
                    "reset",
                    "Reset",
                    class_="p-1"),
                class_="col-2")
        ),
        ui.div(
            ui.div(header_row, *rows, style="width:716px"),
            class_="overflow-auto"),
        class_="mb-3"
    )


@module.server
def payoff_server(input, output, session, df):
    @reactive.Calc
    def payoff():
        n_row = input.n_row()
        n_col = input.n_col()

        data = []
        for i in range(n_row):
            row = []
            for j in range(n_col):
                try:
                    x = parse_expr_safer(input[f"cell_{i}{j}1"](),
                                         transformations="all")
                except Exception as e:
                    msg = f"on the left side of row {i + 1} and column {j + 1}"
                    raise Exception(msg) from e
                try:
                    y = parse_expr_safer(input[f"cell_{i}{j}2"](),
                                         transformations="all")
                except Exception as e:
                    msg = f"on the right side of row {i + 1} and column {j + 1}"
                    raise Exception(msg) from e
                row.append((x, y))
            data.append(row)
        index = [input[f"row_{i}"]() for i in range(n_row)]
        columns = [input[f"column_{i}"]() for i in range(n_col)]

        return pd.DataFrame(data, index, columns)

    @reactive.Effect
    @reactive.event(input.reset)
    def _():
        if not input.reset():
            return
        n_row, n_col = price_war_df.shape
        ui.update_numeric("n_row", value=n_row)
        ui.update_numeric("n_col", value=n_col)
        for i in range(n_col):
            ui.update_text(f"column_{i}", value=str(price_war_df.columns[i]))
        for i in range(n_row):
            ui.update_text(f"row_{i}", value=str(price_war_df.index[i]))
            for j in range(n_col):
                x, y = price_war_df.iloc[i, j]
                ui.update_text(f"cell_{i}{j}1", value=str(x))
                ui.update_text(f"cell_{i}{j}2", value=str(y))

    return payoff


@module.ui
def oligopoly_ui():
    return ui.nav(
        "Oligopoly",
        ui.h1("Oligopoly"),
        ui.div(
            ui.div(
                ui.img(src="http://ncase.me/trust/social/thumbnail.png",
                       class_="w-100 flex-shrink-0 me-3",
                       alt="thumbnail of the game"),
                class_="col-md-4 mb-md-0 p-md-4"),
            ui.div(
                ui.h5("The Evolution of Trust"),
                ui.p("""An interactive guide to the game theory of why & how we
                     trust each other."""),
                ui.a("https://ncase.me/trust/", href="https://ncase.me/trust/",
                     target="_blank", class_="stretched-link"),
                class_="col-md-8 p-4 ps-md-0"),
            class_="row g-0 position-relative border border-3 rounded"
        ),
        ui.h2("Introduction"),
        ui.p("""An oligopoly is a market that contains a small number of firms.
             Because there are only a handful of key producers in the market,
             the decisions of each firm have ramifications for not only itself
             but also for each of its competitors. Given the impact oligopolists
             have on one another, a firm’s strategic choice will typically
             depend on what other firms are doing. This strategic interaction
             between firms is a key feature of oligopoly, not present in perfect
             competition, monopoly, or monopolistic competition."""),
        ui.h2("Characteristic of an oligopoly"),
        ui.markdown(
            """
            Oligopolies have the following characteristics:
            1. **Few sellers and many buyers.** Output in the market is produced
            by a handful of firms.
            2. **Price maker.** Because there are only a small number of firms
            in the market, each firm retains the power to set its own
            prices.
            3. **Barriers to entry.** Entry into the market is difficult as
            there are high barriers to entry.
            4. **Potential product differentiation.** Products may be
            differentiated or not depending on the market.
            """),
        ui.h2("Simultaneous move games"),
        ui.p("""Often firms will need to make strategic decisions without
             knowledge of what other firms in the market have decided to do. In
             such circumstances, firms make decisions as though their choices
             were made simultaneously. In such cases, it will be appropriate to
             analyze the strategic interaction of those firms as a simultaneous
             move game."""),
        ui.h3("Price war"),
        ui.p("""In some cases, the game faced by the firms in an oligopoly might
             resemble a prisoner’s dilemma."""),
        payoff_ui("price_war", price_war_df, max_size=2),
        ui.output_ui("price_war_ui"),
        ui.output_text("price_war_text")
    )


@module.server
def oligopoly_server(input, output, session, settings):
    price_war_payoff = payoff_server("price_war", price_war_df)

    @reactive.Calc
    def price_war_error():
        df = price_war_payoff()
        c1, c2 = map(str.lower, df.columns)
        i1, i2 = map(str.lower, df.index)
        [[[r1, r2], [s1, t1]], [[t2, s2], [p1, p2]]] = df.values

        if c1 != i1 or c2 != i2:
            return ("This is not a prisoner's dilemma. "
                    "Player 1 and player 2 should have the same startegies.")

        hints = []
        if r1 != r2:
            hints.append("Player 1 and player 2 should have the same payoff if "
                         f"they both choose {c1}.")
        if s1 != s2:
            hints.append("Player 1 and player 2 should have the same payoff if "
                         f"they choose {c1} but their opponent chooses {c2}.")
        if t1 != t2:
            hints.append("Player 1 and player 2 should have the same payoff if "
                         f"they choose {c2} but their opponent chooses {c1}.")
        if p1 != p2:
            hints.append("Player 1 and player 2 should have the same payoff if "
                         f"they both choose {c2}.")
        if hints:
            return "This is not a prisoner's dilemma. " + " ".join(hints)

        r, s, t, p = r1, s1, t1, p1
        hints = []
        if r <= p:
            hints.append(f"Mutual cooperation should be superior to mutual "
                         "defection.")
        if t <= r or p <= s:
            hints.append("Defection should be the dominant strategy for both "
                         "agents.")
        if hints:
            return "This is not a prisoner's dilemma. " + " ".join(hints)

    @render.ui
    def price_war_ui():
        def to_latex(cell):
            if isinstance(cell, tuple):
                x, y = cell
                return (
                    latex_approx(x, settings.perc(), settings.approx()),
                    latex_approx(y, settings.perc(), settings.approx()))
            return latex_approx(cell, settings.perc(), settings.approx())
        
        df = price_war_payoff()
        styler = style_tuple_df(df.map(to_latex))

        if not price_war_error():
            def color(_):
                colors = pd.DataFrame(index=df.index, columns=df.columns)
                colors.loc["Low", "Low"] = "background-color: lightgreen"
                return colors
            styler = styler.apply(color, axis=None)

        return ui.HTML(styler.to_html(escape=False))

    @render.text
    def price_war_text():
        if price_war_error():
            return price_war_error()

        df = price_war_payoff()
        c1, c2 = map(str.lower, df.columns)

        return f"""
            This is a prisoner's dilemma. The pure equilibrium (colored green)
            is when both firms choose {c1}, but the profit-maximizing strategy
            for the industry is that they both choose {c2}."""
