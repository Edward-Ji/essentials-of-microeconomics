from shiny import module, reactive, render, req, ui
from sympy import latex, solve, symbols

from module import demand_supply_ui, demand_supply_server
from util import latex_approx, parse_expr_safer


@module.ui
def taxes_and_subsidies_ui():
    return ui.nav(
        "Taxes and subsidies",
        ui.h1("Taxes and subsidies"),
        ui.p("""We will restrict our analysis to taxes and subsidies on
             consumption and production, but it is important to be aware that
             other types of taxes and subsidies also exist."""),
        ui.h2("Taxes"),
        demand_supply_ui("ds"),
        ui.markdown(
            """A _tax_ is a compulsory payment made to the government. We
            consider _per-unit taxes_ which is a fixed amount for each unit; as
            opposed to _ad valorum tax_, where the amount of the tax is a fixed
            percentage.
            """),
        ui.h3("Tax on comsumption"),
        ui.input_text("tc", r"Enter a tax on consumption \(t_c\):", "5"),
        ui.p(r"""Suppose that for every unit purchased, consumers must pay a tax
             of \(t\) to the government in addition to the price to the
             producer. If the demand curve without tax is \(Q=Q(P)\), then the
             demand curve with tax is \(Q=Q(P+t)\). Graphically, the demand
             curve shifts downwards by \(t\) after taxing."""),
        ui.output_text("taxed_demand_text"),
        ui.h3("Tax on production"),
        ui.input_text("tp", r"Enter a tax on production \(t_p\):", "5"),
        ui.p(r"""Suppose that for every unit sold, producers must pay a tax of
             \(t\) to the government in addition to the price to the producer.
             If the supply curve without tax is \(Q=Q(P)\), then the supply
             curve with tax is \(Q=Q(P-t)\). Graphically, the supply curve
             shifts upwards by \(t\) after taxing."""),
        ui.output_text("taxed_supply_text"),
        ui.h3("Effect of tax on welfare"),
        ui.p("""Both consumer surplus and producer surplus will decrease as a
             result of the tax, for two reasons: first, fewer units are traded
             in the market; second, on each unit, consumers pay a higher price
             and producers receive a lower price relative to a market without a
             tax."""),
        ui.output_text("taxed_equilibrium_text"),
        ui.p(r"""The government now receives some surplus in the form of tax
             revenue. The government revenue \(GR\) is the product of the
             per-unit tax \(t\) and the quantity traded under taxes
             \(Q^t\)."""),
        ui.output_text("government_revenue_text"),
        ui.p("""The more elastic the demand or supply curves, the greater the
             effect of the tax on the quantity traded in the market, which will
             result in a greater DWL.""")
    )


@module.server
def taxes_and_subsidies_server(input, output, session, settings):
    symbol_P, symbol_Q = symbols("P, Q", positive=True)

    demand, supply, _, _ = demand_supply_server("ds", settings)

    @reactive.Calc
    def consumer_tax():
        return parse_expr_safer(input.tc(), transformations="all")

    @reactive.Calc
    def producer_tax():
        return parse_expr_safer(input.tp(), transformations="all")

    @reactive.Calc
    def equilibrium():
        solutions = solve([demand(), supply()], symbol_P, symbol_Q, dict=True)
        req(len(solutions) == 1)
        return solutions[0]

    @reactive.Calc
    def taxed_demand():
        return demand().subs(symbol_P, symbol_P + consumer_tax())

    @reactive.Calc
    def taxed_P_d():
        solutions = solve(taxed_demand(), symbol_P)
        req(len(solutions) == 1)
        return solutions[0]

    @reactive.Calc
    def taxed_supply():
        return supply().subs(symbol_P, symbol_P - producer_tax())

    @reactive.Calc
    def taxed_P_s():
        solutions = solve(taxed_supply(), symbol_P)
        req(len(solutions) == 1)
        return solutions[0]

    @reactive.Calc
    def taxed_equilibrium():
        solutions = solve([taxed_demand(), taxed_supply()],
                          symbol_P, symbol_Q,
                          dict=True)
        req(len(solutions) == 1)
        return solutions[0]

    @reactive.Calc
    def Q_taxed():
        return taxed_equilibrium()[symbol_Q]

    @reactive.Calc
    def GR():
        return (consumer_tax() + producer_tax()) * Q_taxed()

    @output
    @render.text
    def taxed_demand_text():
        return (
            r"$$"
            + latex_approx(taxed_demand(), settings.perc(), settings.approx())
            + "$$The inverse demand equation after taxing is $$P_d^t ="
            + latex_approx(taxed_P_d(), settings.perc(), settings.approx())
            + r"$$"
        )

    @output
    @render.text
    def taxed_supply_text():
        return (
            "$$"
            + latex_approx(taxed_supply(), settings.perc(), settings.approx())
            + "$$The inverse supply equation after taxing is $$P_s^t ="
            + latex_approx(taxed_P_s(), settings.perc(), settings.approx())
            + "$$"
        )

    @output
    @render.text
    def taxed_equilibrium_text():
        return (
            r"$$\begin{cases}"
            + latex(taxed_demand()) + r"\\"
            + latex(taxed_supply())
            + r"\end{cases} \implies"
            + r"\\"
            + "Q^t ="
            + latex_approx(Q_taxed(), settings.perc(), settings.approx())
            + "$$")

    @output
    @render.text
    def government_revenue_text():
        return (
            r"$$GR = (t_c + t_p)Q^t ="
            + latex_approx(GR(), settings.perc(), settings.approx())
            + "$$")
