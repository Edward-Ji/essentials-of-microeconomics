import matplotlib.pyplot as plt
import pandas as pd
from shiny import module, reactive, render, req, ui

from util import latex_approx, parse_expr_safer


def ui_col_4(*args):
    return ui.div(*args, class_="col-4")


@module.ui
def trade_and_ppf_ui():
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
            ui_col_4(),
            ui_col_4(ui.input_text("good_a", "", "Pepper mills")),
            ui_col_4(ui.input_text("good_b", "", "Salt shakers"))
        ),
        ui.row(
            ui_col_4(ui.input_text("party_a", "", "Broderick")),
            ui_col_4(ui.input_text("max_a_a", "", "8")),
            ui_col_4(ui.input_text("max_a_b", "", "8"))
        ),
        ui.row(
            ui_col_4(ui.input_text("party_b", "", "Christopher")),
            ui_col_4(ui.input_text("max_b_a", "", "2")),
            ui_col_4(ui.input_text("max_b_b", "", "4"))
        ),
        ui.output_text("abs_adv"),
        ui.p("The opportunity costs of both goods for both parties is "
             "represented in the following table:"),
        ui.output_table("oppo_cost"),
        ui.output_text("comp_adv"),
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
        ui.output_plot("ppf"),
        value="trade_and_ppf"
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
def trade_and_ppf_server(input, output, session, settings):
    def sanitize(name):
        @reactive.Calc
        def wrapper():
            try:
                value = parse_expr_safer(input[name]())
                req(value is not None and value > 0, cancel_output=True)
                return value
            except SyntaxError:
                req(False, cancel_output=True)
                assert False
        return wrapper

    max_a_a, max_a_b, max_b_a, max_b_b = map(
        sanitize, ["max_a_a", "max_a_b", "max_b_a", "max_b_b"])

    @reactive.Calc
    def cost_a_a():
        return max_a_b() / max_a_a()

    @reactive.Calc
    def cost_a_b():
        return max_a_a() / max_a_b()

    @reactive.Calc
    def cost_b_a():
        return max_b_b() / max_b_a()

    @reactive.Calc
    def cost_b_b():
        return max_b_a() / max_b_b()

    @render.text
    def abs_adv():
        return generate_advantage_text(
            input.good_a(), input.good_b(),
            input.party_a(), max_a_a(), max_a_b(),
            input.party_b(), max_b_a(), max_b_b())

    @reactive.Calc
    def oppo_cost_df():
        parties = [input.party_a(), input.party_b()]
        goods = [input.good_a(), input.good_b()]
        return pd.DataFrame([[cost_a_a(), cost_a_b()],
                             [cost_b_a(), cost_b_b()]],
                            index=parties, columns=goods)

    @render.table(index=True)
    def oppo_cost():
        attrs = 'class="dataframe table shiny-table w-auto"'
        def latexify(expr):
            expr = latex_approx(expr, settings.perc(), settings.approx())
            return fr"\({expr}\)"
        return oppo_cost_df().style.set_table_attributes(attrs).format(latexify)

    @render.text
    def comp_adv():
        [max_a_a, max_a_b], [max_b_a, max_b_b] = oppo_cost_df().to_numpy()
        return generate_advantage_text(
            input.good_a(), input.good_b(),
            input.party_a(), max_a_a, max_a_b,
            input.party_b(), max_b_a, max_b_b,
            kind="comparative")

    @render.plot(height=400)
    def ppf():
        party_a = input.party_a()
        party_b = input.party_b()
        good_a = input.good_a()
        good_b = input.good_b()

        if cost_a_a() < cost_b_a():
            mid_a, mid_b, show_dashed = max_a_a(), max_b_b(), True
        elif cost_a_a() == cost_b_a():
            mid_a, mid_b, show_dashed = max_a_a(), max_b_b(), False
        else:
            mid_a, mid_b, show_dashed = max_b_a(), max_a_b(), True

        ax = plt.figure().gca()
        ax.plot((0, max_a_b()), (max_a_a(), 0), label=party_a)
        ax.plot((0, max_b_b()), (max_b_a(), 0), label=party_b)
        ax.plot((0, mid_b, max_a_b() + max_b_b()),
                (max_a_a() + max_b_a(), mid_a, 0),
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
