from dataclasses import dataclass
from shiny import module, reactive, ui

from util import Approx


@dataclass
class Settings:
    style: ...
    approx: ...
    perc: ...


@module.ui
def settings_ui():
    header = (
        ui.h1("Settings", id="settings-modal-label", class_="modal-title fs-5"),
        ui.tags.button(type="button", class_="btn-close",
                       data_bs_dismiss="modal", aria_label="Close settings")
        )
    body = (
        ui.h2("Theme"),
        ui.input_select("theme", "Select theme:", ["Light", "Dark"]),
        ui.h2("Evaluation"),
        ui.input_select("approx", "Numerical evaluation of rationals:",
                        [e.value for e in Approx]),
        ui.panel_conditional(
            f"input.approx !== '{Approx.HIDE.value}'",
            ui.input_slider("perc", "Binary percision:", 0, 100, 15)),
        ui.h2("Input storage"),
        ui.p("""Automatically save inputs when they change or manually save and
             clear inputs. Clear and refresh to reset all inputs to
             default."""),
        ui.div(
            ui.tags.button("Auto",
                           id="input-auto-btn",
                           class_="btn btn-outline-secondary",
                           data_bs_toggle="button"),
            ui.tags.button("Save",
                           id="input-save-btn",
                           class_="btn btn-outline-secondary"),
            ui.tags.button("Clear",
                           id="input-clear-btn",
                           class_="btn btn-outline-danger"),
            class_="btn-group",
            role="group",
            aria_label="Input storage button group")

        )
    return ui.div(
        ui.div(
            ui.div(
                ui.div(*header, class_="modal-header"),
                ui.div(*body, class_="modal-body"),
                class_="modal-content"),
            class_="modal-dialog"),
        id="settings-modal",
        class_="modal fade",
        tabindex="-1",
        aria_labelledby="settings-modal-label",
        aria_hidden="true"
    )


@module.server
def settings_server(input, output, session):
    @reactive.Effect
    def _():
        ui.update_dark_mode(input.theme().lower())

    @reactive.Calc
    def style():
        return "default" if input.theme() != "Dark" else "dark_background"

    @reactive.Calc
    def approx():
        return Approx(input.approx())

    @reactive.Calc
    def perc():
        return input.perc()

    return Settings(style, approx, perc)
