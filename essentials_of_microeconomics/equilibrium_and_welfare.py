import matplotlib.pyplot as plt
from shiny import module, reactive, render, req, ui
from sympy import integrate, latex, plot, simplify, solve, symbols

from module import demand_supply_ui, demand_supply_server
from util import latex_approx


@module.ui
def equilibrium_and_welfare_ui():
    return ui.nav(
        "Equilibrium and welfare",
        ui.h1("Equilibrium and welfare"),
        demand_supply_ui("ds"),
        ui.h2("Equilibrium"),
        ui.p(r"""A market is in equilibrium if, at some market price, the
             quantity \(Q_d\) demanded by consumers equals the quantity \(Q_s\)
             supplied by firms. The price at which this occurs is called the
             market-clearing price (or equilibrium price), denoted \(P^*\)."""),
        ui.output_text("equilibrium_text"),
        ui.h2("Welfare"),
        ui.p("""We can measure the observed changes in the benefits consumers
             and firms gain in the markets using welfare analysis."""),
        ui.h3("Consumer surplus"),
        ui.p("""Consumer surplus (CS) is the welfare consumers receive from
             buying units of goods or services in the market. It is given by the
             consumer’s willingness to pay, minus the price paid, for each unit
             bought. We can find an individual’s CS by calculating the area
             between the demand curve and the price line."""),
        ui.output_text("CS_text"),
        ui.h3("Producer surplus"),
        ui.p("""Producer surplus (PS) is the welfare producers (usually firms)
             receive from selling units of a good or service in the market. It
             is given by the price the producer receives, minus the cost of
             production, for each unit of the good or service bought. We can
             find a firm’s PS by calculating the area between the price line and
             the firm’s supply curve."""),
        ui.output_text("PS_text"),
        ui.h3("Total surplus"),
        ui.p(r"""The total surplus (TS) is the sum of consumer and producer
             surplus in the market equilibrium. TS is the area between the
             demand and supply curves, up to the market equilibrium, quantity
             \(Q^*\)."""),
        ui.output_text("TS_text"),
        ui.output_plot("welfare"),
        value="equilibrium_and_welfare"
    )


@module.server
def equilibrium_and_welfare_server(input, output, session, settings):
    symbol_P, symbol_Q = symbols("P, Q", positive=True)

    demand, supply, P_d, P_s = demand_supply_server("ds", settings)

    @reactive.Calc
    def equilibrium():
        solutions = solve([demand(), supply()], symbol_P, symbol_Q, dict=True)
        req(len(solutions) == 1)
        return solutions[0]

    @reactive.Calc
    def P_optimal():
        return equilibrium()[symbol_P]

    @reactive.Calc
    def Q_optimal():
        return equilibrium()[symbol_Q]

    @reactive.Calc
    def CS():
        return simplify(integrate(P_d() - P_optimal(),
                                  (symbol_Q, 0, Q_optimal())))

    @reactive.Calc
    def PS():
        return simplify(integrate(P_optimal() - P_s(),
                                  (symbol_Q, 0, Q_optimal())))

    @reactive.Calc
    def TS():
        return simplify(CS() + PS())

    @render.text
    def equilibrium_text():
        return (
            r"$$\begin{cases}"
            + latex(demand()) + r"\\"
            + latex(supply())
            + r"\end{cases} \implies \begin{cases}"
            + "P^* ="
            + latex_approx(P_optimal(), settings.perc(), settings.approx())
            + r"\\"
            + "Q^* ="
            + latex_approx(Q_optimal(), settings.perc(), settings.approx())
            + r"\end{cases}$$")

    @render.text
    def CS_text():
        return (r"$$CS = \int_0^{Q^*}P_d - P^*\,dQ ="
                + latex_approx(CS(), settings.perc(), settings.approx())
                + "$$")

    @render.text
    def PS_text():
        return (r"$$PS = \int_0^{Q^*}P^* - P_s\,dQ ="
                + latex_approx(PS(), settings.perc(), settings.approx())
                + "$$")

    @render.text
    def TS_text():
        return (r"$$TS = CS + PS ="
                + latex_approx(TS(), settings.perc(), settings.approx())
                + "$$")

    @render.plot(height=400)
    def welfare():
        ax = plt.subplot()
        plot_d, plot_s = plot(P_d(), P_s(),
                              (symbol_Q, 0, Q_optimal() * 2),
                              show=False)
        plot_cs, plot_ps = plot(P_d(), P_s(),
                                (symbol_Q, 0 ,Q_optimal()),
                                show=False)
        ax.plot(*plot_d.get_points(), label="Demand")
        ax.plot(*plot_s.get_points(), label="Supply")
        ax.scatter(Q_optimal(), P_optimal(), s=50, c="tab:green", marker="o",
                   label="Equilibrium", zorder=100)
        ax.fill_between(*plot_cs.get_points(), float(P_optimal()),
                        alpha=.5, label="CS")
        ax.fill_between(*plot_ps.get_points(), float(P_optimal()),
                        alpha=.5, label="PS")
        ax.set_xlim(0)
        ax.set_ylim(0)
        ax.set_xlabel("$Q$")
        ax.set_ylabel("$P$")
        ax.legend()
        return ax
