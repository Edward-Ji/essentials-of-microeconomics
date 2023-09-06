from shiny import module, reactive, render, req, ui
from sympy import Eq, integrate, latex, parse_expr, solve, symbols
from common import mathjax_script


@module.ui
def equilibrium_and_welfare_ui():
    return ui.nav(
        "Equilibrium and welfare",
        ui.h1("Equilibrium and welfare"),
        ui.row(
            ui.column(5,
                ui.input_text("ew_Q_d",
                              r"Enter an expression for demand curve:",
                              value="Q = 50 - P/2")
            ),
            ui.column(5, ui.output_ui("ew_P_d"))
        ),
        ui.row(
            ui.column(5,
                ui.input_text("ew_Q_s",
                              r"Enter an expression for supply curve:",
                              value="Q = P - 5")
            ),
            ui.column(5, ui.output_ui("ew_P_s"))
        ),
        ui.h2("Equilibrium"),
        ui.p(r"""A market is in equilibrium if, at some market price, the
             quantity \(Q_d\) demanded by consumers equals the quantity \(Q_s\)
             supplied by firms. The price at which this occurs is called the
             market-clearing price (or equilibrium price), denoted \(P^*\)."""),
        ui.output_ui("ew_equilibrium"),
        ui.h2("Welfare"),
        ui.p("""We can measure the observed changes in the benefits consumers
             and firms gain in the markets using welfare analysis."""),
        ui.h3("Consumer surplus"),
        ui.p("""Consumer surplus (CS) is the welfare consumers receive from
             buying units of goods or services in the market. It is given by the
             consumer’s willingness to pay, minus the price paid, for each unit
             bought. We can find an individual’s CS by calculating the area
             between the demand curve and the price line."""),
        ui.output_ui("ew_CS"),
        ui.h3("Producer surplus"),
        ui.p("""Producer surplus (PS) is the welfare producers (usually firms)
             receive from selling units of a good or service in the market. It
             is given by the price the producer receives, minus the cost of
             production, for each unit of the good or service bought. We can
             find a firm’s PS by calculating the area between the price line and
             the firm’s supply curve."""),
        ui.output_ui("ew_PS"),
        ui.h3("Total surplus"),
        ui.p(r"""The total surplus (TS) is the sum of consumer and producer
             surplus in the market equilibriuma. TS is the area between the
             demand and supply curves, up to the market equilibrium, quantity
             \(Q^*\)."""),
        ui.output_ui("ew_TS")
    )


@module.server
def equilibrium_and_welfare_server(input, output, session):
    symbol_P, symbol_Q = symbols("P, Q", positive=True)

    @reactive.Calc
    def demand():
        return parse_expr(input.ew_Q_d(), {"P": symbol_P, "Q": symbol_Q},
                          transformations="all")

    @reactive.Calc
    def P_d():
        solutions = solve(demand(), symbol_P)
        req(len(solutions) == 1)
        return solutions[0]

    @reactive.Calc
    def supply():
        return parse_expr(input.ew_Q_s(), {"P": symbol_P, "Q": symbol_Q},
                          transformations="all")

    @reactive.Calc
    def P_s():
        solutions = solve(supply(), symbol_P)
        req(len(solutions) == 1)
        return solutions[0]

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

    @output
    @render.ui
    def ew_P_d():
        return ui.div(
            ui.p("Inverse demand equation: $$P_d = " + latex(P_d()) + "$$"),
            mathjax_script)

    @output
    @render.ui
    def ew_P_s():
        return ui.div(
            ui.p("Inverse supply function: $$P_s = " + latex(P_s()) + "$$"),
            mathjax_script)


    @output
    @render.ui
    def ew_equilibrium():
        return ui.div(
            ui.p(r"$$\begin{cases}"
                 + latex(demand()) + r"\\"
                 + latex(supply())
                 + r"\end{cases} \implies \begin{cases}"
                 + "P^* =" + latex(P_optimal()) + r"\\"
                 + "Q^* =" + latex(Q_optimal())
                 + r"\end{cases}$$"),
            mathjax_script)

    @output
    @render.ui
    def ew_CS():
        return ui.div(
            ui.p(r"$$CS = \int_0^{Q^*}P_d - P^*\,dQ =" + latex(CS()) + "$$"),
            mathjax_script)

    @output
    @render.ui
    def ew_PS():
        return ui.div(
            ui.p(r"$$PS = \int_0^{Q^*}P^* - P_s\,dQ =" + latex(PS()) + "$$"),
            mathjax_script)

    @output
    @render.ui
    def ew_TS():
        return ui.div(
            ui.p(r"$$TS = CS + PS =" + latex(TS()) + "$$"),
            mathjax_script)
