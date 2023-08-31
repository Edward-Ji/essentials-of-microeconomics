from shiny import App, ui
from common import mathjax_script
from tp import tp_ui, tp_server
from pc import pc_ui, pc_server

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
        tp_ui("tp"),
        pc_ui("pc"),
        ui.nav_spacer(),
        ui.nav_control(
            ui.a("GitHub",
                 href="https://github.com/Edward-Ji/EssentialsOfMicroeconomics",
                 target="_blank")
        ),
        selected="Production and costs"
    )
)


def server(input, output, session):
    tp_server("tp")
    pc_server("pc")


app = App(app_ui, server)
