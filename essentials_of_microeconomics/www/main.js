$(window).bind("load", function() {
    for (id in localStorage) {
        var element = $("#" + id);
        if (element.hasClass("js-range-slider")) {
            var data = element.data("ionRangeSlider");
            data.update({from: localStorage[id]});
        } else {
            element.val(localStorage[id]);
        }
        Shiny.setInputValue(id, localStorage[id]);
    }
})

$(document).on("change", "[class*='shiny-bound-input']", function() {
    localStorage.setItem($(this).attr("id"), $(this).val());

/* MathJax */
$("#MathJax-script").on("load", function() {
    MathJax.typeset();
});
