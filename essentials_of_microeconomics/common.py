from shiny import ui

mathjax_script = ui.tags.script(
    "if (window.MathJax) MathJax.Hub.Queue(['Typeset', MathJax.Hub]);")
