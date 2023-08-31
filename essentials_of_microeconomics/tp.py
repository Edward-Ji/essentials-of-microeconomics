from fractions import Fraction
import pandas as pd
import matplotlib.pyplot as plt
from shiny import module, reactive, render, ui

@module.ui
def tp_ui():
    return ui.nav(
        "Trade and PPF",
        ui.h1("Trade and PPF"),
        ui.h2("Absolute and comparative advantage"),
        ui.p("""Party A has an absolute advantage over Party B in the production
             of a good if, for a given amount of resources, A can produce a
             greater number of that good than B."""),
        ui.p("""Party A has a comparative advantage over Party B in the
             production of a good if A’s opportunity cost of producing that good
             is lower than B’s opportunity cost."""),
        ui.p("For example, two parties spend some fixed time making two goods:"),
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
        ui.output_text("tp_comp_adv"),
        ui.p("""Trade is determined by the comparative advantage, not the
             absolute advantage. Trade allows parties to specialize in producing
             the good in which they have the lower opportunity cost and increase
             the total output."""),
        ui.h2("PPF"),
        ui.p("""A production possibility frontier (PPF) graphs the output that
             an individual can produce with a particular set of resources."""),
        ui.tags.ul(
            ui.tags.li("""It draws the set of possible output choices when these
                       resources are used efficiently."""),
            ui.tags.li("""Production efficiency is achieved when it’s not
                       possible to produce more of one good without producing
                       less of some other goods."""),
            ui.tags.li("""Points inside the PPF are inefficient and points
                       outside are infeasible.""")
        ),
        ui.p("""The shape of an agent’s PPF is determined by its level of
             resources and technology. If there’s an increase in the resources
             or improvement in technology to produce both goods, the PPF will
             shift outwards from the origin in both axes. A rotation is when a
             shock boosts the production of one good. If the agent doesn’t
             trade, the PPF also describes the agent’s consumption choices."""),
        ui.p("""The slope of the tangent of the PPF at any point measures the
             opportunity cost of producing an extra unit of a good in terms of
             the other. Notice that when the PPF should be concave, i.e., the
             opportunity cost of some goods is increasing in its level of
             output. This is because some resources are more suited for the
             production of other goods."""),
        ui.p("""In our example, the PPF of both parties and their joint PPF is
             as follows: """),
        ui.output_plot("tp_ppf", width="400px")
    )

def generate_advantage_text(
        good_a, good_b,
        party_a, max_a_a, max_a_b,
        party_b, max_b_a, max_b_b,
        kind="absolute"):
    if max_a_a > max_b_a:
        party_adv_a = party_a
    elif max_a_a == max_b_a:
        party_adv_a = None
    else:
        party_adv_a = party_b
    if max_a_b > max_b_b:
        party_adv_b = party_a
    elif max_a_b == max_b_b:
        party_adv_b = None
    else:
        party_adv_b = party_b

    if party_adv_a == party_adv_b:
        if party_adv_a is None:
            party_adv_a = "Neither"
        text = (
            f"{party_adv_a.title()} has the {kind} advantage in the production "
            f"of both {good_a} and {good_b}.")
    else:
        text = ""
        if party_adv_a is None:
            text += (
                f"Neither has the {kind} advantage in the production of "
                f"{good_a}. ")
        else:
            text += (
                f"{party_adv_a.title()} has the {kind} advantage in the "
                f"production of {good_a}. ")
        if party_adv_b is None:
            text += (
                f"Neither has the {kind} advantage in the production of "
                f"{good_b}.")
        else:
            text += (
                f"{party_adv_b.title()} has the {kind} advantage in the "
                f"production of {good_b}.")
    return text

@module.server
def tp_server(input, output, session):
    @output
    @render.text
    def tp_abs_adv():
        return generate_advantage_text(
            input.tp_good_a(), input.tp_good_b(),
            input.tp_party_a(), input.tp_max_a_a(), input.tp_max_a_b(),
            input.tp_party_b(), input.tp_max_b_a(), input.tp_max_b_b())

    @reactive.Calc
    def oppo_cost_df():
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
    @render.table(index=True)
    def tp_oppo_cost():
        return oppo_cost_df()

    @output
    @render.text
    def tp_comp_adv():
        [max_a_a, max_a_b], [max_b_a, max_b_b] = oppo_cost_df().to_numpy()
        return generate_advantage_text(
            input.tp_good_a(), input.tp_good_b(),
            input.tp_party_a(), max_a_a, max_a_b,
            input.tp_party_b(), max_b_a, max_b_b,
            kind="comparative")

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
            mid_a, mid_b, show_dashed = max_a_a, max_b_b, True
        elif max_a_a / max_a_b == max_b_a / max_b_b:
            mid_a, mid_b, show_dashed = max_a_a, max_b_b, False
        else:
            mid_a, mid_b, show_dashed = max_b_a, max_a_b, True

        ax = plt.figure().gca()
        ax.plot((0, max_a_b), (max_a_a, 0), label=party_a)
        ax.plot((0, max_b_b), (max_b_a, 0), label=party_b)
        ax.plot((0, mid_b, max_a_b + max_b_b), (max_a_a + max_b_a, mid_a, 0),
                label="Joint")
        if show_dashed:
            ax.hlines(mid_a, 0, mid_b, colors="grey", linestyles="dashed")
            ax.vlines(mid_b, 0, mid_a, colors="grey", linestyles="dashed")
        ax.set_xlabel(good_b)
        ax.set_ylabel(good_a)
        ax.set_xlim(0)
        ax.set_ylim(0)
        ax.legend()
        return ax
