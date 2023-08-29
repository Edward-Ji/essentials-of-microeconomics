from shiny import App, ui
from tp import tp_ui, tp_server

app_ui = ui.page_fluid(
    ui.navset_tab(
        tp_ui("tp")
    )
)


def server(input, output, session):
    tp_server("tp")


app = App(app_ui, server)
