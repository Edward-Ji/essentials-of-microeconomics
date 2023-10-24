from shiny import module, reactive, render, req, ui
from sympy import solve, symbols

from util import latex_approx, parse_expr_safer


@module.ui
def demand_supply_ui():
    return ui.TagList(
        ui.row(
            ui.column(6,
                ui.input_text("Q_d",
                              r"Enter an expression for demand curve:",
                              value="Q = 50 - P/2")
            ),
            ui.column(6, ui.output_ui("P_d_text"))
        ),
        ui.row(
            ui.column(6,
                ui.input_text("Q_s",
                              r"Enter an expression for supply curve:",
                              value="Q = P - 5")
            ),
            ui.column(6, ui.output_ui("P_s_text"))
        ),
    )


@module.server
def demand_supply_server(input, output, session, settings):
    symbol_P, symbol_Q = symbols("P, Q", positive=True)

    @reactive.Calc
    def demand():
        return parse_expr_safer(input.Q_d(), {"P": symbol_P, "Q": symbol_Q},
                                transformations="all")

    @reactive.Calc
    def P_d():
        solutions = solve(demand(), symbol_P)
        req(len(solutions) == 1)
        return solutions[0]

    @reactive.Calc
    def supply():
        return parse_expr_safer(input.Q_s(), {"P": symbol_P, "Q": symbol_Q},
                                transformations="all")

    @reactive.Calc
    def P_s():
        solutions = solve(supply(), symbol_P)
        req(len(solutions) == 1)
        return solutions[0]

    @output
    @render.ui
    def P_d_text():
        return ("Inverse demand equation: $$P_d = "
                + latex_approx(P_d(), settings.perc(), settings.approx())
                + "$$")

    @output
    @render.text
    def P_s_text():
        return ("Inverse supply function: $$P_s = "
                + latex_approx(P_s(), settings.perc(), settings.approx())
                + "$$")

    return demand, supply, P_d, P_s
