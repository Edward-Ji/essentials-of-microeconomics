from pathlib import Path

import numpy as np
from shiny import App, ui
from trade_and_ppf import trade_and_ppf_ui, trade_and_ppf_server
from production_and_costs import (
        production_and_costs_ui, production_and_costs_server)
from equilibrium_and_welfare import (
        equilibrium_and_welfare_ui, equilibrium_and_welfare_server)
from elasticity import elasticity_ui, elasticity_server

np.seterr(divide="ignore", invalid="ignore")

app_ui = ui.page_navbar(
    ui.head_content(
        ui.tags.link(
            rel="stylesheet",
            href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css"
        ),
        ui.tags.link(rel="stylesheet", href="/main.css"),
        ui.tags.script(
            src="https://mathjax.rstudio.com/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML"
        )
    ),
    trade_and_ppf_ui("tp"),
    production_and_costs_ui("pc"),
    equilibrium_and_welfare_ui("ew"),
    elasticity_ui("el"),
    ui.nav_spacer(),
    ui.nav_control(
        ui.a(ui.tags.i(class_="bi bi-github", style=""),
             href="https://github.com/Edward-Ji/EssentialsOfMicroeconomics",
             target="_blank")
    ),
    title="Essentials of Microeconomics",
    position="fixed-top",
    lang="en"
)


def server(input, output, session):
    def mathjax():
        ui.insert_ui(
            ui.tags.script("if (window.MathJax)"
                           "MathJax.Hub.Queue(['Typeset', MathJax.Hub]);"),
            "body"
        )
        ui.remove_ui("body > script")
    session.on_flush(mathjax)
    session.on_flushed(mathjax, once=False)

    trade_and_ppf_server("tp")
    production_and_costs_server("pc")
    equilibrium_and_welfare_server("ew")
    elasticity_server("el")


www_dir = Path(__file__).parent.resolve() / "www"

app = App(app_ui, server, static_assets=www_dir)
