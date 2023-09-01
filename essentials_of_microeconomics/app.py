from shiny import App, ui
from common import mathjax_script
from trade_and_ppf import trade_and_ppf_ui, trade_and_ppf_server
from production_and_costs import (
        production_and_costs_ui, production_and_costs_server)

app_ui = ui.page_fluid(
    ui.head_content(
        ui.tags.style("""div.tab-pane {
            max-width: 800px;
            margin: auto;
        }"""),
        ui.tags.script(
            src="https://mathjax.rstudio.com/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML"
        ),
        mathjax_script
    ),
    ui.navset_tab(
        trade_and_ppf_ui("tp"),
        production_and_costs_ui("pc"),
        ui.nav_spacer(),
        ui.nav_control(
            ui.a("GitHub",
                 href="https://github.com/Edward-Ji/EssentialsOfMicroeconomics",
                 target="_blank")
        ),
    )
)


def server(input, output, session):
    trade_and_ppf_server("tp")
    production_and_costs_server("pc")


app = App(app_ui, server)
