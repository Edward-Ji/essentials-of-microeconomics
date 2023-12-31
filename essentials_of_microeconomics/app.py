from pathlib import Path

import numpy as np
from shiny import App, ui

from trade_and_ppf import trade_and_ppf_ui, trade_and_ppf_server
from production_and_costs import (
    production_and_costs_ui,
    production_and_costs_server
)
from equilibrium_and_welfare import (
    equilibrium_and_welfare_ui,
    equilibrium_and_welfare_server
)
from elasticity import elasticity_ui, elasticity_server
from monopoly import monopoly_ui, monopoly_server
from oligopoly import oligopoly_server, oligopoly_ui
from taxes_and_subsidies import (
    taxes_and_subsidies_ui,
    taxes_and_subsidies_server
)
from externalities import externalities_ui, externalities_server
from settings import settings_server, settings_ui

np.seterr(divide="ignore", invalid="ignore")

app_ui = ui.page_navbar(
    ui.head_content(
        ui.tags.title("Essentials of Microeconomics"),
        ui.tags.link(rel="apple-touch-icon", sizes="180x180",
                     href="/apple-touch-icon.png"),
        ui.tags.link(rel="icon", type="image/png", sizes="32x32",
                     href="/favicon-32x32.png"),
        ui.tags.link(rel="icon", type="image/png", sizes="16x16",
                     href="/favicon-16x16.png"),
        ui.tags.link(rel="manifest", href="/manifest.json"),
        ui.tags.link(
            rel="stylesheet",
            href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css"
        ),
        ui.tags.link(rel="stylesheet", href="/main.css"),
        ui.tags.script(
            src="https://polyfill.io/v3/polyfill.min.js?features=es6"),
        ui.tags.script(
            id="MathJax-script", async_=True,
            src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"),
        ui.tags.script(src="/main.js")
    ),
    trade_and_ppf_ui("trade_and_ppf"),
    ui.nav_menu(
        "Market fundamentals",
        production_and_costs_ui("production_and_costs"),
        equilibrium_and_welfare_ui("equilibrium_and_welfare"),
        elasticity_ui("elasticity")
    ),
    ui.nav_menu(
        "Types of market",
        monopoly_ui("monopoly"),
        oligopoly_ui("oligopoly")
    ),
    ui.nav_menu(
        "Market failures",
        taxes_and_subsidies_ui("taxes_and_subsidies"),
        externalities_ui("externalities")
    ),
    ui.nav_spacer(),
    ui.nav_control(
        ui.a(ui.tags.i(class_="bi bi-gear-fill", style=""), type_="button",
             data_bs_toggle="modal", data_bs_target="#settings-modal")),
    ui.nav_control(
        ui.a(ui.tags.i(class_="bi bi-github", style=""),
             href="https://github.com/Edward-Ji/essentials-of-microeconomics",
             target="_blank")),
    footer=settings_ui("settings"),
    title=ui.img(src="favicon-32x32.png"),
    position="fixed-top",
    lang="en"
)


def server(input, output, session):
    def mathjax():
        ui.insert_ui(ui.tags.script("MathJax.typeset()"), "body")
        ui.remove_ui("body > script")

    session.on_flush(mathjax)
    session.on_flushed(mathjax, once=False)

    settings = settings_server("settings")
    trade_and_ppf_server("trade_and_ppf", settings)
    production_and_costs_server("production_and_costs", settings)
    equilibrium_and_welfare_server("equilibrium_and_welfare", settings)
    elasticity_server("elasticity", settings)
    monopoly_server("monopoly", settings)
    oligopoly_server("oligopoly", settings)
    taxes_and_subsidies_server("taxes_and_subsidies", settings)
    externalities_server("externalities", settings)


www_dir = Path(__file__).parent.resolve() / "www"

app = App(app_ui, server, static_assets=www_dir)
