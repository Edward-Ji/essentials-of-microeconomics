from typing import cast

from pandas.io.formats.style import plt
from shiny import module, reactive, render, req, ui
from sympy import S, integrate, latex, plot, solve, symbols

from module import demand_supply_ui, demand_supply_server
from util import latex_approx, parse_expr_safer


@module.ui
def externalities_ui():
    return ui.nav(
        "Externalities",
        ui.h1("Externalities"),
        ui.h2("Introduction"),
        ui.markdown(
            """Competitive markets are usually Pareto efficient in the long run.
            In contrast, the situations where the market outcome is not
            efficient are called _market failures_. One type of market failure
            is externalities.
            """),
        ui.h2("External costs and benefits"),
        demand_supply_ui("demand_supply"),
        ui.markdown(
            """An *externality* is a cost or benefit that accrues to a person
            who is not directly involved in an economic activity or transaction.
            These costs or benefits are also known as “external costs” or
            “external benefits”.
            """),
        ui.markdown(
            """A *positive externality* occurs when the economic activity
            results in external benefits for a third party. A *negative
            externality* occurs when the economic activity results in external
            costs for a third party.
            """),
        ui.h2("Positive externalities"),
        ui.row(
            ui.column(6,
                ui.input_text("marginal_external_benefit",
                              r"Enter an expression for \(MEB\):",
                              value="Q / 2")),
            ui.column(6, ui.output_text("marginal_external_benefit_text"))),
        ui.markdown(
            """Consumers derive benefits from consuming goods. However, in the
            presence of a positive externality, the consumption or production of
            the good also has external benefits for a third party. Hence, the
            benefit to society as a whole must include both the consumer’s
            benefit and the external benefit.
            """),
        ui.markdown(
            f"""The marginal benefit to society of an additional unit of the good
            is known as the *marginal social benefit (MSB)*. It is made up of
            the *marginal private benefit (MPB)* enjoyed by the consumer and the
            *marginal external benefit (MEB)* that accrues to a third party.
            """),
        ui.output_text("marginal_social_benefit_text"),
        ui.h2("Negative externalities"),
        ui.row(
            ui.column(6, ui.input_text("marginal_external_cost",
                                        r"Enter an expression for \(MEC\):",
                                        value="0")),
            ui.column(6, ui.output_text("marginal_external_cost_text"))),
        ui.markdown(
            """Similarly, producers incur costs from producing goods. However,
            in the presence of a negative externality, the consumption or
            production of the good also has external costs for a third party.
            Hence, the cost to society as a whole must include both the
            producer’s cost and the external cost.
            """),
        ui.markdown(
            f"""The marginal cost to society of an additional unit of the good is
            known as the *marginal social cost (MSC)*. It is made up of the
            *marginal private cost (MPC)* incurred by the producer and the
            *marginal external cost (MEC)* that accrues to a third party.
            """),
        ui.output_text("marginal_social_cost_text"),
        ui.h2("The problem with externalities"),
        ui.markdown(
            """Externalities are a source of market failure because they
            represent external costs or benefits not accounted for by the
            market. Because consumers only account for their private benefits
            and producers only account for their private costs, the market
            equilibrium is determined by the private demand and supply curves.
            $$
            MPB=MPC
            $$
            """),
        ui.output_text("market_equilibrium_text"),
        ui.markdown(
            """However, from the perspective of society as a whole, any external
            costs and benefits associated with the consumption or production of
            the good should also be taken into account. Hence the socially
            optimal equilibrium is determined by the marginal social benefit and
            cost curves.
            $$
            MSB=MSC
            $$
            """),
        ui.output_text("socially_optimal_equilibrium_text"),
        ui.p("""The DWL indicates the surplus forgone in the market equilibrium
             relative to the efficient outcome
             """),
        ui.output_text("deadweight_loss_text"),
        ui.output_plot("externalities")
        )


@module.server
def externalities_server(input, output, session, settings):
    symbol_P, symbol_Q = symbols("P, Q", positive=True)

    demand, supply, MPB, MPC = demand_supply_server("demand_supply", settings)

    @reactive.Calc
    def MEB():
        try:
            return parse_expr_safer(input.marginal_external_benefit(),
                                    {"Q": symbol_Q},
                                    transformations="all")
        except SyntaxError:
            req(False, cancel_output=True)
            assert False

    @reactive.Calc
    def MSB():
        return S(MPB() + MEB())

    @reactive.Calc
    def MEC():
        try:
            return parse_expr_safer(input.marginal_external_cost(),
                                    {"Q": symbol_Q},
                                    transformations="all")
        except SyntaxError:
            req(False, cancel_output=True)
            assert False

    @reactive.Calc
    def MSC():
        return S(MPC() + MEC())

    @reactive.Calc
    def market_equilibrium():
        solutions = solve([demand(), supply()], symbol_P, symbol_Q, dict=True)
        req(len(solutions) == 1)
        return solutions[0]

    @reactive.Calc
    def P_market():
        return market_equilibrium()[symbol_P]

    @reactive.Calc
    def Q_market():
        return market_equilibrium()[symbol_Q]

    @reactive.Calc
    def socially_optimal_equilibrium():
        solutions = solve([symbol_P - MSB(), symbol_P - MSC()],
                          symbol_P, symbol_Q, dict=True)
        req(len(solutions) == 1)
        return solutions[0]

    @reactive.Calc
    def P_optimal():
        return socially_optimal_equilibrium()[symbol_P]

    @reactive.Calc
    def Q_optimal():
        return socially_optimal_equilibrium()[symbol_Q]

    @reactive.Calc
    def deadweight_loss():
        return S(integrate(MSB() - MSC(), (symbol_Q, Q_market(), Q_optimal())))

    @render.text
    def marginal_external_benefit_text():
        return ("$$MEB ="
                + latex_approx(MEB(), settings.perc(), settings.approx())
                + "$$")

    @render.text
    def marginal_social_benefit_text():
        return ("$$MSB = MPB + MEB ="
                + latex_approx(MSB(), settings.perc(), settings.approx())
                + "$$")


    @render.text
    def marginal_external_cost_text():
        return ("$$MEC ="
                + latex_approx(MEC(), settings.perc(), settings.approx())
                + "$$")

    @render.text
    def marginal_social_cost_text():
        return ("$$MSC = MPC + MEC ="
                + latex_approx(MSC(), settings.perc(), settings.approx())
                + "$$")

    @render.text
    def market_equilibrium_text():
        return ("It solves to the following:"
                r"$$\begin{cases}"
                + latex(demand()) + r"\\"
                + latex(supply())
                + r"\end{cases} \implies \begin{cases}"
                + "P^m ="
                + latex_approx(P_market(), settings.perc(), settings.approx())
                + r"\\"
                + "Q^m ="
                + latex_approx(Q_market(), settings.perc(), settings.approx())
                + r"\end{cases}$$")

    @render.text
    def socially_optimal_equilibrium_text():
        return ("It solves to the following:"
                r"$$\begin{cases}"
                + "P =" + latex(MSB()) + r"\\"
                + "P =" + latex(MSC())
                + r"\end{cases} \implies \begin{cases}"
                + "P^* ="
                + latex_approx(P_optimal(), settings.perc(), settings.approx())
                + r"\\"
                + "Q^* ="
                + latex_approx(Q_optimal(), settings.perc(), settings.approx())
                + r"\end{cases}$$")

    @render.text
    def deadweight_loss_text():
        if Q_optimal() < Q_market():
            formula = r"\int_{Q^*}^{Q^m}MSB - MSC\,dQ"
        else:
            formula = r"\int_{Q^m}^{Q^*}MSC - MSB\,dQ"
        return ("$$DWL =" + formula + "="
                + latex_approx(deadweight_loss(), settings.perc(),
                               settings.approx())
                + "$$")

    @render.plot
    def externalities():
        Q_m, P_m = float(Q_market()), float(P_market())
        Q_o, P_o = float(Q_optimal()), float(P_optimal())
        Q_lim = 2 * max(Q_m, Q_o)

        line_props = {"color": "grey", "linestyle": "dashed"}
        ax = plt.subplot()

        # plot marginal social benefit/cost curves
        plot_msb = plot(MSB(), (symbol_Q, 0, Q_lim), show=False)
        plot_msc = plot(MSC(), (symbol_Q, 0, Q_lim), show=False)
        ax.plot(*plot_msb[0].get_points(), label="MSB")
        ax.plot(*plot_msc[0].get_points(), label="MSC")

        # plot marginal private profit/cost curves
        if not MEB().is_zero:
            plot_mpb = plot(MPB(), (symbol_Q, 0, Q_lim), show=False)
            ax.plot(*plot_mpb[0].get_points(), label="MPB")
        if not MEC().is_zero:
            plot_mpc = plot(MPC(), (symbol_Q, 0, Q_lim), show=False)
            ax.plot(*plot_mpc[0].get_points(), label="MPC")

        # plot reference lines and set ticks for key points
        ax.vlines(Q_o, 0, P_o, **line_props)
        ax.hlines(P_o, 0, Q_o, **line_props)
        if not MEB().is_zero or not MEC().is_zero:
            ax.vlines(Q_m, 0, P_m, **line_props)
            ax.hlines(P_m, 0, Q_m, **line_props)
            ax.set_xticks(cast(list, [Q_m, Q_o]), ["$Q^m$", "$Q^*$"])
            ax.set_yticks(cast(list, [P_m, P_o]), ["$P^m$", "$P^*$"])
        else:
            ax.set_xticks(cast(list, [Q_o]), ["$Q^*$"])
            ax.set_yticks(cast(list, [P_o]), ["$P^*$"])

        # plot deadweight loss region
        plot_dwl = plot(MSB(), MSC(), (symbol_Q, Q_m , Q_o), show=False)
        ax.fill_between(plot_dwl[0].get_points()[0],
                        plot_dwl[0].get_points()[1],
                        plot_dwl[1].get_points()[1],
                        color="grey", alpha=.5, label="DWL")

        ax.set_xlim(0)
        ax.set_ylim(0)
        ax.set_xlabel("$Q$")
        ax.set_ylabel("$P$")
        ax.legend()

