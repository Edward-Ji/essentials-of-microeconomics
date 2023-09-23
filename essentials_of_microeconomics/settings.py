from dataclasses import dataclass
from shiny import module, reactive, ui

from util import Approx


@dataclass
class Settings:
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
        ui.input_select("approx", "Numerical evaluation of rationals:",
                        [e.value for e in Approx]),
        ui.panel_conditional(
            f"input.approx !== '{Approx.HIDE.value}'",
            ui.input_slider("perc", "Binary percision:", 0, 100, 15))
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
    @reactive.Calc
    def approx():
        return Approx(input.approx())

    @reactive.Calc
    def perc():
        return input.perc()

    return Settings(approx, perc)
