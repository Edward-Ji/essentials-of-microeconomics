from fractions import Fraction
import pandas as pd
import matplotlib.pyplot as plt
from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.navset_tab(
        ui.nav(
            "Trade and PPF",
            ui.p("Two parties spend some fixed time making two goods:"),
            ui.row(
                ui.column(2),
                ui.column(2, ui.input_text("tp_good_a", "", "Pepper mills")),
                ui.column(2, ui.input_text("tp_good_b", "", "Salt shakers")),
            ),
            ui.row(
                ui.column(2, ui.input_text("tp_party_a", "", "Broderick")),
                ui.column(2, ui.input_numeric("tp_max_a_a", "", 8, min=1)),
                ui.column(2, ui.input_numeric("tp_max_a_b", "", 8, min=1)),
            ),
            ui.row(
                ui.column(2, ui.input_text("tp_party_b", "", "Christopher")),
                ui.column(2, ui.input_numeric("tp_max_b_a", "", 2, min=1)),
                ui.column(2, ui.input_numeric("tp_max_b_b", "", 4, min=1)),
            ),
            ui.output_text("tp_abs_adv"),
            ui.p("The opportunity costs of both goods for both parties is "
                 "represented in the following table:"),
            ui.output_table("tp_oppo_cost"),
            ui.p("The PPF of both parties and their joint PPF is as follows: "),
            ui.output_plot("tp_ppf", width="50%")
        )
    )
)


def server(input, output, session):
    @output
    @render.text
    def tp_abs_adv():
        if input.tp_max_a_a() > input.tp_max_b_a():
            party_adv_a = input.tp_party_a()
        elif input.tp_max_a_a() == input.tp_max_b_a():
            party_adv_a = None
        else:
            party_adv_a = input.tp_party_b()
        if input.tp_max_a_b() > input.tp_max_b_b():
            party_adv_b = input.tp_party_a()
        elif input.tp_max_a_b() == input.tp_max_b_b():
            party_adv_b = None
        else:
            party_adv_b = input.tp_party_b()

        good_a = input.tp_good_a().lower()
        good_b = input.tp_good_b().lower()

        if party_adv_a == party_adv_b:
            if party_adv_a is None:
                party_adv_a = "Neither"
            text = (
                f"{party_adv_a} has the absolute advantage in the production of "
                f"both {good_a} and {good_b}.")
        else:
            text = ""
            if party_adv_a is None:
                text += (
                    f"Neither has the absolute advantage in the production of "
                    f"{good_a}. ")
            else:
                text += (
                    f"{party_adv_a} has the absolute advantage in the "
                    f"production of {good_a}. ")
            if party_adv_b is None:
                text += (
                    f"Neither has the absolute advantage in the production of "
                    f"{good_b}.")
            else:
                text += (
                    f"{party_adv_b} has the absolute advantage in the "
                    f"production of {good_b}.")
        return text

    @output
    @render.table(index=True)
    def tp_oppo_cost():
        max_a_a = input.tp_max_a_a()
        max_a_b = input.tp_max_a_b()
        max_b_a = input.tp_max_b_a()
        max_b_b = input.tp_max_b_b()
        cost_a_a = Fraction(max_a_b, max_a_a)
        cost_a_b = Fraction(max_a_a, max_a_b)
        cost_b_a = Fraction(max_b_b, max_b_a)
        cost_b_b = Fraction(max_b_a, max_b_b)
        parties = [input.tp_party_a(), input.tp_party_b()]
        goods = [input.tp_good_a(), input.tp_good_b()]
        return pd.DataFrame([[cost_a_a, cost_a_b], [cost_b_a, cost_b_b]],
                            index=parties, columns=goods)

    @output
    @render.plot()
    def tp_ppf():
        max_a_a = input.tp_max_a_a()
        max_a_b = input.tp_max_a_b()
        max_b_a = input.tp_max_b_a()
        max_b_b = input.tp_max_b_b()
        party_a = input.tp_party_a()
        party_b = input.tp_party_b()
        good_a = input.tp_good_a()
        good_b = input.tp_good_b()

        if max_a_a / max_a_b > max_b_a / max_b_b:
            mid_a, mid_b = max_a_b, max_b_b
        else:
            mid_a, mid_b = max_b_a, max_a_a

        fig, ax = plt.subplots()
        ax: plt.Axes
        ax.plot((0, max_a_b), (max_a_a, 0), label=party_a)
        ax.plot((0, max_b_b), (max_b_a, 0), label=party_b)
        ax.plot((0, mid_b, max_a_b + max_b_b), (max_a_a + max_b_a, mid_a, 0),
                label="Joint")
        ax.hlines(mid_a, 0, mid_b, colors="grey", linestyles="dashed")
        ax.vlines(mid_b, 0, mid_a, colors="grey", linestyles="dashed")
        ax.set_xlabel(good_b)
        ax.set_ylabel(good_a)
        ax.set_xlim(0)
        ax.set_ylim(0)
        ax.legend()
        return fig


app = App(app_ui, server)
