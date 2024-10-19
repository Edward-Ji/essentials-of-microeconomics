from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
from shiny import module, reactive, render, req, ui
from sympy import integrate, latex, plot, solve, symbols

from module import demand_supply_server, demand_supply_ui
from util import latex_approx, parse_expr_safer, styled_plot


@module.ui
def taxes_and_subsidies_ui():
    return ui.nav_panel(
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
        ui.p(r"""The deadweight loss (DWL) is the loss in total surplus due to
             the tax. It is the area between the demand and supply curves from
             the quantity traded under taxes \(Q^t\) to the quantity traded
             without taxes \(Q^*\)."""),
        ui.output_text("deadweight_loss_text"),
        ui.output_plot("tax_plot"),
        ui.p("""The more elastic the demand or supply curves, the greater the
             effect of the tax on the quantity traded in the market, which will
             result in a greater DWL."""),
        ui.h3("Incidences of tax"),
        ui.markdown(
            """The _legal incidence of the tax_ refers to who is legally
            responsible for paying the tax. By contrast, the _economic incidence
            of the tax_ refers to who, as a matter of fact, actually bears the
            burden of the tax. As a general rule, the legal incidence of the tax
            doesn’t necessarily bear all the economic incidence of the tax.
            The economic incidence of the tax is determined solely by the
            relative elasticities of the demand and supply curves."""),
        ui.output_text("tax_incidence_text"),
        value="taxes_and_subsidies"
    )


@module.server
def taxes_and_subsidies_server(input, output, session, settings):
    symbol_P, symbol_Q = symbols("P, Q", positive=True)

    demand, supply, P_d, P_s = demand_supply_server("ds", settings)

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
    def P_optimal():
        return equilibrium()[symbol_P]

    @reactive.Calc
    def Q_optimal():
        return equilibrium()[symbol_Q]

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
    def P_taxed_consumer():
        return P_d().subs(symbol_Q, Q_taxed())

    @reactive.Calc
    def P_taxed_producer():
        return P_s().subs(symbol_Q, Q_taxed())

    @reactive.Calc
    def GR():
        return (consumer_tax() + producer_tax()) * Q_taxed()

    @reactive.Calc
    def DWL():
        return integrate(P_d() - P_s(), (symbol_Q, Q_taxed(), Q_optimal()))

    @render.text
    def taxed_demand_text():
        return (
            r"$$"
            + latex_approx(taxed_demand(), settings.perc(), settings.approx())
            + "$$The inverse demand equation after taxing is $$P_d ="
            + latex_approx(taxed_P_d(), settings.perc(), settings.approx())
            + r"$$"
        )

    @render.text
    def taxed_supply_text():
        return (
            "$$"
            + latex_approx(taxed_supply(), settings.perc(), settings.approx())
            + "$$The inverse supply equation after taxing is $$P_s ="
            + latex_approx(taxed_P_s(), settings.perc(), settings.approx())
            + "$$"
        )

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

    @render.text
    def government_revenue_text():
        return (
            r"$$GR = (t_c + t_p)Q^t ="
            + latex_approx(GR(), settings.perc(), settings.approx())
            + "$$")

    @render.text
    def deadweight_loss_text():
        return (
            r"$$DWL = \int_{Q^t}^{Q^*}P_d - P_s ="
            + latex_approx(DWL(), settings.perc(), settings.approx())
            + "$$")

    @styled_plot(settings)
    def tax_plot():
        Q_lim = 2 * max(Q_optimal(), Q_taxed())
        Q_t = float(Q_taxed())
        P_p_t, P_c_t = float(P_taxed_producer()), float(P_taxed_consumer())
        Q_o, P_o = float(Q_optimal()), float(P_optimal())

        line_props = {"color": "grey", "linestyle": "dashed"}
        ax = plt.subplot()

        # plot demand and supply curves
        plot_d, plot_s = plot(P_d(), P_s(), (symbol_Q, 0, Q_lim), show=False)
        plot_cs, plot_ps = plot(P_d(), P_s(), (symbol_Q, 0 , Q_t), show=False)
        plot_dwl = plot(P_d(), P_s(), (symbol_Q, Q_t , Q_o), show=False)
        ax.plot(*plot_d.get_points(), label="Demand")
        ax.plot(*plot_s.get_points(), label="Supply")

        # plot reference lines and set ticks for key points
        ax.vlines(Q_t, 0, max(P_c_t, P_p_t), **line_props)
        ax.vlines(Q_o, 0, P_o, **line_props)
        ax.hlines([P_c_t, P_p_t], 0, Q_t, **line_props)
        ax.set_xticks([Q_t, Q_o], ["$Q^t$", "$Q^*$"])
        ax.set_yticks([P_c_t, P_p_t], ["$P_c^t$", "$P_p^t$"])

        # plot welfare regions
        ax.fill_between(plot_cs.get_points()[0],
                        plot_cs.get_points()[1],
                        P_c_t, alpha=.5, label="CS")
        ax.fill_between(plot_ps.get_points()[0],
                        plot_ps.get_points()[1],
                        P_p_t, alpha=.5, label="PS")
        ax.add_patch(Rectangle((0, P_p_t), Q_t, P_c_t - P_p_t,
                               color="green", alpha=.5, label="GR"))
        ax.fill_between(plot_dwl[0].get_points()[0],
                        plot_dwl[0].get_points()[1],
                        plot_dwl[1].get_points()[1],
                        color="grey", alpha=.5, label="DWL")

        ax.set_xlim(0)
        ax.set_ylim(0)
        ax.set_xlabel("$Q$")
        ax.set_ylabel("$P$")
        ax.legend()

        return ax

    @render.text
    def tax_incidence_text():
        if consumer_tax().is_zero and producer_tax().is_zero:
            return """
                No tax is imposed. Neither the consumer nor the producer bears
                the legal or economic incidence of the tax."""

        text = "The government imposes a tax of "
        if not consumer_tax().is_zero:
            text += (
                r"\(t_c ="
                + latex_approx(consumer_tax(),
                               settings.perc(),
                               settings.approx())
                + r"\) on consumers")
            if not producer_tax().is_zero:
                text += (
                    r" and a tax of \(t_p ="
                    + latex_approx(producer_tax(),
                                   settings.perc(),
                                   settings.approx())
                    + r"\) on producers")
        else:
            if not producer_tax().is_zero:
                text += (
                    r"\(t_p ="
                    + latex_approx(producer_tax(),
                                   settings.perc(),
                                   settings.approx())
                    + r"\) on producers")
        text += ". "

        text += "The legal incidence of the tax is on "
        if not consumer_tax().is_zero and not producer_tax().is_zero:
            text += "both consumers and producers. "
        elif not consumer_tax().is_zero:
            text += "consumers. "
        else:
            text += "producers. "

        P_p_t, P_c_t = P_taxed_producer(), P_taxed_consumer()
        text += (
            "$$"
            + r"\begin{align*}"
            + "P_c^t &= P_d(Q^t) ="
            + latex_approx(P_c_t, settings.perc(), settings.approx())
            + r"\\"
            + "P_p^t &= P_s(Q^t) ="
            + latex_approx(P_p_t, settings.perc(), settings.approx())
            + r"\end{align*}"
            + "$$"
        )

        consumer_tax_burden = P_c_t - P_optimal()
        producer_tax_burden = P_optimal() - P_p_t
        if not consumer_tax_burden.is_zero:
            text += (
                r"Consumers pay an extra \(P_c^t - P^* ="
                + latex_approx(consumer_tax_burden,
                               settings.perc(),
                               settings.approx())
                + r"\) per unit")
            if not producer_tax_burden.is_zero:
                text += (
                    r" and producers receive \(P^* - P_s^t ="
                    + latex_approx(producer_tax_burden,
                                   settings.perc(),
                                   settings.approx())
                    + r"\) less per unit")

        else:
            if not producer_tax_burden.is_zero:
                text += (
                    r"Producers receive \(P^* - P_s^t ="
                    + latex_approx(producer_tax_burden,
                                   settings.perc(),
                                   settings.approx())
                    + r"\) less per unit")
        text += ". "

        text += "The economic incidence of the tax is on "
        if not consumer_tax_burden.is_zero and not producer_tax_burden.is_zero:
            text += "both consumers and producers. "
        elif not consumer_tax_burden.is_zero:
            text += "consumers. "
        else:
            text += "producers. "

        return text
