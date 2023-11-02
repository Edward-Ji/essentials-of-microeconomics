import matplotlib.pyplot as plt
from shiny import module, reactive, render, ui
from sympy import (
    Function,
    Q,
    ask,
    assuming,
    diff,
    latex,
    plot,
    simplify,
    symbols,
)

from util import latex_approx, parse_expr_safer


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
        ui.row(
            ui.column(6, ui.input_text(
                "q", r"Enter an expression for output \(q(L)\):",
                value="K^(1/2)L^(1/2)")),
            ui.column(6, ui.output_text("q_text"))
        ),
        ui.h3("Marginal product"),
        ui.p("""The marginal product (MP) of some input refers to how output
             responds when there is a change in the number of that specific
             input used. This is a short-run concept."""),
        ui.output_text("MP_text"),
        ui.p("""If the MP becomes progressively smaller as we increase the use
             of that input, this is called diminishing marginal product; If the
             MP becomes larger, this is called increasing marginal product."""),
        ui.output_text("dMP_text"),
        ui.p("Diminishing MP is thought to be very common."),
        ui.h3("Returns to scale"),
        ui.p("""Returns to scale refer to how the number of outputs changes when
             there is a proportional change in the quantity of all inputs. If
             the output increases by the same proportional change, there are
             constant returns to scale. If the output increases by more (less)
             than the proportional increase in all inputs, there are increasing
             (decreasing) returns to scale. Returns to scale is a long-run
             concept."""),
        ui.output_text("rts_text"),
        ui.h2("Short-run costs"),
        ui.p("""To use the inputs of production and transform them into outputs,
             a firm will have to incur some costs, which may include:"""),
        ui.tags.ul(
            ui.tags.li("wages paid to workers,"),
            ui.tags.li("cost of leasing, or"),
            ui.tags.li("purchasing factories and machines.")),
        ui.p(r"""A cost function is an equation \(TC=f(q)\) that links the
             quantity of outputs with its associated production cost."""),
        ui.tags.ul(
            ui.tags.li(r"""When the output is \(0\), the total cost is strictly
                       positive."""),
            ui.tags.li(r"""The total cost curve rises as output increases,
                       \(MP>0\)."""),
            ui.tags.li(r"""The total cost curve rises at an increasing rate,
                       \(MP'<0\).""")),
        ui.row(
            ui.column(6, ui.input_text("TC",
                                       r"Enter an expression for \(TC = f(q)\):",
                                       value="100+20q+q^2")),
            ui.column(6, ui.output_text("TC_text"))
        ),
        ui.h3("Fixed and variable costs"),
        ui.p("""Fixed costs (FC) are costs that do not vary with the quantity of
             output produced."""),
        ui.output_text("FC_text"),
        ui.p("""Variable costs (VC) are those costs that vary with or depend on
             the quantity of output produced."""),
        ui.output_text("VC_text"),
        ui.h3("Marginal cost"),
        ui.p("""The marginal cost (MC) is the increase in total cost that arises
             from an extra unit of production."""),
        ui.output_text("MC_text"),
        ui.p("""Due to diminishing MP, a typical MC curve will eventually
             increase with increasing output."""),
        ui.h3("Average costs"),
        ui.p("Average fixed cost (AFC) is a fixed cost per unit of output:"),
        ui.output_text("AFC_text"),
        ui.p("Note that it is always downward-sloping."),
        ui.hr(style="margin-block-start: 0.5em; margin-block-end: 0.5em;"),
        ui.p("""Average variable cost (AVC) is the variable cost per unit of
             output:"""),
        ui.output_text("AVC_text"),
        ui.p("""Because AVC is affected by diminishing MP, the AVC curve will
             eventually be upward-sloping over output."""),
        ui.hr(style="margin-block-start: 0.5em; margin-block-end: 0.5em;"),
        ui.p("Average total cost (ATC) is the total cost per unit of output:"),
        ui.output_text("ATC_text"),
        ui.p("""The decline in AFC usually dominates at low input levels, but at
             higher ones, AVC will dominate. This makes the ATC curve a
             U-shape."""),
        ui.output_plot("costs"),
        ui.p("The MC curve intersects the AVC curves at the minimum of AVC."),
        ui.h2("Long-run costs"),
        ui.h3("Long-run marginal cost"),
        ui.p("""In the long run, all inputs can be varied to increase one unit
             of output produced. Hence, for the same level of output, long-run
             marginal cost will be less than or equal to short-run marginal
             cost."""),
        ui.h3("Long-run average cost"),
        ui.p("""For the same reason, the long-run average cost can be no greater
             than the short-run average cost. The long-run average cost curve
             will be the lower envelope of all of the short-run average cost
             curves."""),
        ui.p("""If long-run average costs are decreasing with output, this is
             called economies of scale. If long-run average costs are increasing
             with output, this is known as diseconomies of scale.""")
    )


@module.server
def production_and_costs_server(input, output, session, settings):
    L, q = symbols("L, q", positive=True)

    @reactive.Calc
    def q_L():
        return parse_expr_safer(input.q(), {"L": L}, transformations="all")

    @reactive.Calc
    def MP():
        return diff(q_L(), L)

    @reactive.Calc
    def dMP():
        return diff(MP(), L)

    @output
    @render.text
    def q_text():
        return (r"$$q = "
                + latex_approx(q_L(), settings.perc(), settings.approx())
                + "$$")

    @output
    @render.text
    def MP_text():
        return (r"$$MP = \frac{dq}{dL} = "
                + latex_approx(MP(), settings.perc(), settings.approx())
                + "$$")

    @output
    @render.text
    def dMP_text():
        with assuming(*(Q.positive(sym) for sym in dMP().free_symbols)):
            if ask(Q.positive(dMP())):
                i = 0
            elif ask(Q.negative(dMP())):
                i = 1
            else:
                i = 2
        text = [
            "We have increasing marginal product:",
            "We have diminishing marginal product:",
            "We have neither diminishing nor increasing marginal product:"
        ][i]
        positivity = [">0", "<0", ""][i]
        return (text
                + r"$$MP' = \frac{dMP}{dL} = "
                + latex_approx(dMP(), settings.perc(), settings.approx())
                + positivity + "$$")

    @output
    @render.text
    def rts_text():
        q2 = q_L().subs({sym: 2 * sym for sym in q_L().free_symbols})
        func = Function("q")(*q_L().free_symbols)
        func2 = Function("q")(*(2 * sym for sym in q_L().free_symbols))
        prop = simplify(q2 / q_L())
        try:
            if prop < 2:
                text = "There is decreasing return to scale:"
            elif prop == 2:
                text = "There is constant return to scale:"
            else:
                text = "There is increasing return to scale:"
        except TypeError:
            text = "The return to scale can not be easily classified:"
        return (
            text + "\n"
            + r"$$\begin{align*}"
            + latex(func2) + "&="
            + latex_approx(q2, settings.perc(), settings.approx()) + r"\\"
            + r"\frac{" + latex(func2) + "}{" + latex(func) + "}&="
            + latex_approx(prop, settings.perc(), settings.approx())
            + r"\end{align*}$$")

    @reactive.Calc
    def TC():
        return parse_expr_safer(input.TC(), {"q": q}, transformations="all")

    @reactive.Calc
    def FC():
        return TC().subs({q: 0})

    @reactive.Calc
    def VC():
        return TC() - FC()

    @reactive.Calc
    def MC():
        return diff(VC(), q)

    @reactive.Calc
    def AFC():
        return simplify(FC() / q)

    @reactive.Calc
    def AVC():
        return simplify(VC() / q)

    @reactive.Calc
    def ATC():
        return simplify(AFC() + AVC())

    @output
    @render.text
    def TC_text():
        return (r"$$TC ="
                + latex_approx(TC(), settings.perc(), settings.approx())
                + "$$")

    @output
    @render.text
    def FC_text():
        return (r"$$FC = f(0) ="
                + latex_approx(FC(), settings.perc(), settings.approx())
                + "$$")

    @output
    @render.text
    def VC_text():
        return (r"$$VC = TC - FC ="
                + latex_approx(VC(), settings.perc(), settings.approx())
                + "$$")

    @output
    @render.text
    def MC_text():
        return (r"$$MC = \frac{dTC}{dq} = \frac{dVC}{dq} ="
                + latex_approx(MC(), settings.perc(), settings.approx())
                + "$$")

    @output
    @render.text
    def AFC_text():
        return (r"$$AFC = \frac{FC}{q} ="
                + latex_approx(AFC(), settings.perc(), settings.approx())
                + "$$")

    @output
    @render.text
    def AVC_text():
        return (r"$$AVC = \frac{VC}{q} ="
                + latex_approx(AVC(), settings.perc(), settings.approx())
                + "$$")

    @output
    @render.text
    def ATC_text():
        return (r"$$ATC = \frac{TC}{q} = AFC + AVC ="
                + latex_approx(ATC(), settings.perc(), settings.approx())
                + "$$")

    @output
    @render.plot(height=400)
    def costs():
        ax = plt.subplot()
        labels = ["MC", "AFC", "AVC", "ATC"]
        plots = plot(MC(), AFC(), AVC(), ATC(), (q, 1, 5), show=False)
        for p, label in zip(plots, labels):
            ax.plot(*p.get_points(), label=label)
        ax.set_xlabel("$q$")
        ax.set_ylabel("costs")
        ax.legend()
        return ax
