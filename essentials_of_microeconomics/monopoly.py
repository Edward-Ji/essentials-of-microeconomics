from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
from shiny import module, reactive, render, req, ui
from sympy import diff, integrate, latex, plot, simplify, solve, symbols

from util import latex_approx, parse_expr_safer


@module.ui
def monopoly_ui():
    return ui.nav(
        "Monopoly",
        ui.h1("Monopoly"),
        ui.p("""A market with one seller is a monopoly, and that seller is a
             monopolist. The market power of a monopolist allows it to charge
             higher prices in order to increase its profits and have
             implications on welfare."""),
        ui.h2("Characteristics of a monopoly"),
        ui.p("Monopolies have the following characteristics:"),
        ui.tags.ol(
            ui.tags.li(
                ui.tags.b("One seller and many buyers. "),
                ui.tags.span(
                    "There is a single producer of all output in the market.")),
            ui.tags.li(
                ui.tags.b("Price maker. "),
                ui.tags.span(
                    """Because the monopolist is the only firm in the market, it
                    has the market power to determine the price in the market -
                    that is, it is a price maker.""")),
            ui.tags.li(
                ui.tags.b("Barriers to entry. "),
                ui.tags.span(
                    """Firms that might like to enter the market are prevented
                    from doing so by barriers to entry."""))
            ),
        ui.h2("Single-price monopolist"),
        ui.h3("Marginal revenue"),
        ui.row(
            ui.column(6,
                ui.input_text("demand",
                              r"Enter an equation for demand curve:",
                              value="P = 360 - 2Q")
            ),
            ui.column(6, ui.output_text("demand_text"))
        ),
        ui.p(r"""Marginal revenue is the firm's additional revenue from selling
             odemandne extra unit of a good."""),
        ui.output_text("marginal_revenue_text"),
        ui.h3("Profit maximization"),
        ui.row(
            ui.column(6,
                ui.input_text("total_cost",
                              r"Enter a formula for total cost:",
                              value="300 + 10Q + Q^2/2")
            ),
            ui.column(6, ui.output_text("total_cost_text"))
        ),
        ui.output_text("marginal_cost_text"),
        ui.p(r"Profit is defined as \(\pi=TR-TC\)."),
        ui.p("""Assuming that profit is concave down, we take the first
             derivative and set it to zero to maximize profit."""),
        ui.p(r"$$\frac{d\pi}{dQ}=\frac{dTR}{dQ}-\frac{dTC}{dQ}=MR-MC=0$$"),
        ui.p("Rearranging gives us the ",
             ui.tags.b("profit-maximizing condition"),
             "."),
        ui.p("$$MR=MC$$"),
        ui.output_text("monopoly_text"),
        ui.p(r"""The maximum profit can be written as the area of a rectangle.
             $$
             \pi^m = P^m \cdot Q^m - ATC^m \cdot Q^m
             = (P^m - ATC^m) \cdot Q^m
             $$"""),
        ui.output_text("monopoly_profit_text"),
        ui.output_plot("monopoly_plot"),
        ui.h2("Welfare under the single-price monopolist"),
        ui.p(r"""The market equilibrium (competitive quantity) is \(Q=Q^*\) such
             that \(MB=MC\). The monopoly quantity is \(Q=Q^m\) such that
             \(MR=MC\). Note that as \(MB>MR\) for all units \(Q>0\), the
             monopolist sells less than the competitive market quantity, i.e.,
             \(Q^m>Q^*\)."""),
        ui.h3("Consumer and producer surplus"),
        ui.p("""The consumer surplus is given by the area below the demand curve
             and above the price line (given by monopoly quantity) for all units
             traded."""),
        ui.output_text("consumer_surplus_text"),
        ui.p("""The producer surplus is given by the area below the price line
             and above the supply curve (given by monopoly quantity) for all
             units traded."""),
        ui.output_text("producer_surplus_text"),
        ui.p("""The monopolist’s producer surplus is larger than that of a
             competitive market."""),
        ui.h3("Total revenue and deadweight loss"),
        ui.p(r"""The total surplus is given by \(TS = CS + PS = \int_0^{Q^m} P_d
             - P_s \,dQ\). Because \(Q^m > Q^*\), the total surplus under a
             monopoly is smaller than that in a competitive market. The gains
             from trade for units between \(Q^m\) and \(Q^*\) are not realized;
             We refer to the lost welfare as deadweight loss (DWL)."""),
        ui.output_text("deadweight_loss_text"),
        value="monopoly"
    )


@module.server
def monopoly_server(input, output, session, settings):
    symbol_p, symbol_q = symbols("P, Q", positive=True)

    @reactive.Calc
    def demand():
        try:
            eq = parse_expr_safer(input.demand(),
                                  {"P": symbol_p, "Q": symbol_q},
                                  transformations="all")
        except SyntaxError:
            req(False, cancel_output=True)
        else:
            solutions = solve(eq, symbol_p, dict=True)
            req(len(solutions) == 1, cancel_output=True)
            return solutions[0][symbol_p]

    @reactive.Calc
    def total_revenue():
        return demand() * symbol_q

    @reactive.Calc
    def marginal_revenue():
        return diff(total_revenue(), symbol_q)

    @reactive.Calc
    def total_cost():
        try:
            return parse_expr_safer(input.total_cost(),
                                    {"Q": symbol_q},
                                    transformations="all")
        except SyntaxError:
            req(False, cancel_output=True)

    @reactive.Calc
    def marginal_cost():
        return diff(total_cost(), symbol_q)

    @reactive.Calc
    def average_total_cost():
        return total_cost() / symbol_q

    @reactive.Calc
    def monopoly_quantity():
        solutions = solve(marginal_revenue() - marginal_cost(),
                          symbol_q,
                          dict=True)
        req(len(solutions) == 1)
        return solutions[0][symbol_q]

    @reactive.Calc
    def monopoly_price():
        return demand().subs({symbol_q: monopoly_quantity()})

    @reactive.Calc
    def monopoly_atc():
        return average_total_cost().subs({symbol_q: monopoly_quantity()})

    @reactive.Calc
    def monopoly_profit():
        return (monopoly_price() - monopoly_atc()) * monopoly_quantity()

    @reactive.Calc
    def consumer_surplus():
        return simplify(integrate(demand() - monopoly_price(),
                                  (symbol_q, 0, monopoly_quantity())))

    @reactive.Calc
    def producer_surplus():
        return simplify(integrate(monopoly_price() - marginal_cost(),
                                  (symbol_q, 0, monopoly_quantity())))

    @reactive.Calc
    def competitive_quantity():
        solutions = solve(demand() - marginal_cost(),
                          symbol_q,
                          dict=True)
        req(len(solutions) == 1)
        return solutions[0][symbol_q]

    @reactive.Calc
    def deadweight_loss():
        return simplify(integrate(
            demand() - marginal_cost(),
            (symbol_q, monopoly_quantity(), competitive_quantity())))

    @render.text
    def demand_text():
        return (
            "$$P = "
            + latex_approx(demand(), settings.perc(), settings.approx())
            + "$$")

    @render.text
    def marginal_revenue_text():
        return (
            r"$$MR = \frac{dTR}{dQ} = \frac{d}{dQ}PQ ="
            + latex_approx(marginal_revenue(), settings.perc(), settings.approx())
            + "$$")

    @render.text
    def total_cost_text():
        return (
            "$$TC = "
            + latex_approx(total_cost(), settings.perc(), settings.approx())
            + "$$")

    @render.text
    def marginal_cost_text():
        return (
            r"Recall the formula for marginal cost. $$MC = \frac{dTC}{dQ} ="
            + latex_approx(marginal_cost(), settings.perc(), settings.approx())
            + "$$")

    @render.text
    def monopoly_text():
        return (
            r"""Substituting and solving gives us the profit-maximizing price
            and quantity, which we denote as \(P^M\) and \(Q^M\) respectively.
            $$"""
            + latex(marginal_revenue()) + "=" + latex(marginal_cost())
            + r"\implies \begin{cases}"
            + "P^m = " + latex_approx(monopoly_price(),
                                      settings.perc(),
                                      settings.approx()) + r"\\"
            + "Q^m = " + latex_approx(monopoly_quantity(),
                                      settings.perc(),
                                      settings.approx())
            + r"\end{cases}$$")

    @render.text
    def monopoly_profit_text():
        return (
            r"$$\pi^m ="
            + latex_approx(monopoly_profit(),
                           settings.perc(),
                           settings.approx())
            + "$$")

    @render.text
    def consumer_surplus_text():
        return (
            r"$$CS = \int_0^{Q^m} P_d - P^m \,dQ ="
            + latex_approx(consumer_surplus(),
                           settings.perc(),
                           settings.approx())
            + "$$"
        )

    @render.text
    def producer_surplus_text():
        return (
            r"$$PS = \int_0^{Q^m} P^m - MC \,dQ ="
            + latex_approx(producer_surplus(),
                           settings.perc(),
                           settings.approx())
            + "$$"
        )

    @render.text
    def deadweight_loss_text():
        return (
            r"$$DWL ="
            + latex_approx(deadweight_loss(),
                           settings.perc(),
                           settings.approx())
            + "$$"
        )

    @render.plot(height=400)
    def monopoly_plot():
        demand_plot, atc_plot, mc_plot, mr_plot = plot(
            demand(), average_total_cost(), marginal_cost(), marginal_revenue(),
            (symbol_q, 0, 2 * monopoly_quantity()),
            show=False)
        q_m = float(monopoly_quantity())
        p_m = float(monopoly_price())
        atc_m = float(average_total_cost().subs({symbol_q: q_m}))
        mc_m = float(marginal_cost().subs({symbol_q: q_m}))
        p_top = max(monopoly_price(), mc_m, atc_m)

        line_props = {"color": "grey", "linestyle": "dashed"}
        ax = plt.subplot()
        ax.plot(*demand_plot.get_points(), label="Demand")
        ax.plot(*atc_plot.get_points(), label="ATC")
        ax.plot(*mr_plot.get_points(), label="MR")
        ax.plot(*mc_plot.get_points(), label="MC")
        ax.vlines(monopoly_quantity(), 0, p_top, **line_props)
        ax.hlines(monopoly_price(), 0, monopoly_quantity(), **line_props)
        ax.hlines(atc_m, 0, monopoly_quantity(), **line_props)
        ax.hlines(mc_m, 0, monopoly_quantity(), **line_props)
        ax.add_patch(Rectangle([0, atc_m], q_m, p_m - atc_m,
                               color="lightgrey", label="Profit"))
        ax.legend()
        ax.set_ylim(0, 2 * float(monopoly_price()))
        ax.set_xlim(0)
        ax.set_xticks([q_m], ["$Q^m$"])
        ax.set_yticks([p_m, atc_m], ["$P^m$", "$ATC^m$"])
        ax.set_xlabel("$Q$")
        ax.set_ylabel("$P$")
        return ax
