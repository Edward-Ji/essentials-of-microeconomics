from shiny import module, reactive, render, req, ui
from sympy import diff, latex, parse_expr, solve, symbols

from util import latex_approx


@module.ui
def monopoly_ui(): return ui.nav(
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
        ui.p(r"Recall that profit is $$\pi=TR-TC$$"),
        ui.p("""Assuming that profit is concave down, we take the first
             derivative and set it to zero to maximize profit:"""),
        ui.p(r"$$\frac{d\pi}{dQ}=\frac{dTR}{dQ}-\frac{dTC}{dQ}=MR-MC=0$$"),
        ui.p("Rearranging gives us the profit-maximizing condition:"),
        ui.p("$$MR=MC$$"),
        ui.output_text("monopoly_text"),
    )


@module.server
def monopoly_server(input, output, session, settings):
    symbol_p, symbol_q = symbols("P, Q", positive=True)

    @reactive.Calc
    def demand():
        eq = parse_expr(input.demand(),
                        {"P": symbol_p, "Q": symbol_q},
                        transformations="all")
        solutions = solve(eq, symbol_p, dict=True)
        req(len(solutions) == 1)
        return solutions[0][symbol_p]

    @reactive.Calc
    def total_revenue():
        return demand() * symbol_q

    @reactive.Calc
    def marginal_revenue():
        return diff(total_revenue(), symbol_q)

    @reactive.Calc
    def total_cost():
        return parse_expr(input.total_cost(),
                          {"Q": symbol_q},
                          transformations="all")

    @reactive.Calc
    def marginal_cost():
        return diff(total_cost(), symbol_q)

    @reactive.Calc
    def monopoly_quantity():
        solutions = solve(marginal_revenue() - marginal_cost(),
                          symbol_q,
                          dict=True)
        req(len(solutions) == 1)
        return solutions[0][symbol_q]

    def monopoly_price():
        return demand().subs({symbol_q: monopoly_quantity()})

    @output
    @render.text
    def demand_text():
        return (
            "$$P = "
            + latex_approx(demand(), settings.perc(), settings.approx())
            + "$$")

    @output
    @render.text
    def marginal_revenue_text():
        return (
            r"$$MR = \frac{dTR}{dQ} = \frac{d}{dQ}PQ ="
            + latex_approx(marginal_revenue(), settings.perc(), settings.approx())
            + "$$")

    @output
    @render.text
    def total_cost_text():
        return (
            "$$TC = "
            + latex_approx(total_cost(), settings.perc(), settings.approx())
            + "$$")

    @output
    @render.text
    def marginal_cost_text():
        return (
            r"Recall that marginal cost is $$MC = \frac{dTC}{dQ} ="
            + latex_approx(marginal_cost(), settings.perc(), settings.approx())
            + "$$")

    @output
    @render.text
    def monopoly_text():
        return (
            r"""Substituting and solving,
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
