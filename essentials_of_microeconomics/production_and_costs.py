from sympy import Q, Function, ask, assuming, diff, latex, parse_expr, symbols
from shiny import Session, module, reactive, render, ui
from common import mathjax_script


@module.ui
def production_and_costs_ui():
    return ui.nav(
        "Production and costs",
        ui.h1("Production and Costs"),
        ui.p("""Using the available technology, a firm converts inputs - usually
             more than one of labor, machines (often called capital), and
             natural resources (typically called land) - into output sold in the
             marketplace."""),
        ui.h2("The short-run and long-run"),
        ui.p("""The short run is the period during which at least one of the
             factors of production is fixed, i.e., the level of input used
             cannot be changed regardless of the output produced. In the long
             run, all factors of production are variable. Note that the
             difference is not in the set time of production, but in how long it
             takes for all of a firm’s inputs to become variable."""),
        ui.h2("Production"),
        ui.p("""A production function shows the relationship between the
             quantity of inputs used and the (maximum) produced amount of
             output, given the state of technology."""),
        ui.h3("Marginal product"),
        ui.row(
            ui.column(5, ui.input_text("pc_q",
                                       r"Enter an expression for \(q(L)\):",
                                       value="K^(1/2)L^(1/2)")),
            ui.column(5, ui.output_ui("pc_q"))
        ),
        ui.p("""The marginal product (MP) of some input refers to how output
             responds when there is a change in the number of that specific
             input used. This is a short-run concept."""),
        ui.output_ui("pc_MP"),
        ui.p("""If the MP becomes progressively smaller as we increase the use
             of that input, this is called diminishing marginal product; If the
             MP becomes larger, this is called increasing marginal product."""),
        ui.output_ui("pc_dMP"),
        ui.p("Diminishing MP is thought to be very common."),
        ui.h3("Returns to scale"),
        ui.p("""Returns to scale refer to how the number of outputs changes when
             there is a proportional change in the quantity of all inputs. If
             the output increases by the same proportional change, there are
             constant returns to scale. If the output increases by more (less)
             than the proportional increase in all inputs, there are increasing
             (decreasing) returns to scale. Returns to scale is a long-run
             concept."""),
        ui.output_ui("pc_rts"),
    )


@module.server
def production_and_costs_server(input, output, session: Session):
    L = symbols("L", positive=True)

    @reactive.Calc
    def q():
        return parse_expr(input.pc_q(), {"L": L}, transformations="all")

    @reactive.Calc
    def MP():
        return diff(q(), L)

    @reactive.Calc
    def MP_():
        return diff(MP(), L)

    @output
    @render.ui
    def pc_q():
        return ui.div(
            ui.p(r"$$q = " + latex(q()) + "$$"),
            mathjax_script)

    @output
    @render.ui
    def pc_MP():
        return ui.div(
            ui.p(r"$$MP = \frac{\Delta q}{\Delta L} = " + latex(MP()) + "$$"),
            mathjax_script)

    @output
    @render.ui
    def pc_MP_():
        if simplify(MP_()).is_positive:
            positivity = r" \ge 0"
        elif simplify(MP_()).is_negative:
            positivity = r" \le 0"
        else:
            positivity = ""
        return ui.div(
            ui.p(r"$$MP' = \frac{\Delta MP}{\Delta L} = "
                 + latex(MP_()) + positivity + "$$"),
            mathjax_script)
