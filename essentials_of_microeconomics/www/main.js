/* Settings and input storage */
function getStorageJSON(key) {
    if (localStorage[key] === undefined) return {};
    try {
        return JSON.parse(localStorage[key]);
    } catch (e) {
        return {};
    }
}

function setStorageJSON(key, id, value) {
    var obj = getStorageJSON(key);
    obj[id] = value;
    localStorage[key] = JSON.stringify(obj);
}

function setValues(dict) {
    for (id in dict) {
        var element = $("#" + id);
        if (element.hasClass("js-range-slider")) {
            var data = element.data("ionRangeSlider");
            data.update({from: dict[id]});
        } else {
            element.val(dict[id]);
        }
        Shiny.setInputValue(id, dict[id]);
    }
}

function loadSettings() {
    var settings = getStorageJSON("settings");
    setValues(settings);
}

function saveSettingsBind() {
    $("[class*='shiny-bound-input'][id|='settings']")
        .on("shiny:inputchanged", function(){
            setStorageJSON("settings", $(this).attr("id"), $(this).val());
        });
}

function loadInput() {
    var input = getStorageJSON("input");
    setValues(input);
}

function saveInput() {
    var input = {};
    $("[class*='shiny-bound-input']")
        .each(function(index) {
            var id = $(this).attr("id");
            var value = Shiny.shinyapp.$inputValues[id];
            input[id] = value;
        });
    localStorage.setItem("input", JSON.stringify(input));
}

function saveInputEvent(event) {
    setStorageJSON("input", $(this).attr("id"), $(this).val());
}

function saveInputBind() {
    $("[class*='shiny-bound-input']")
        .not("[id|='settings']")
        .on("shiny:inputchanged", saveInputEvent);
}

function saveInputUnbind() {
    $("[class*='shiny-bound-input']")
        .not("[id|='settings']")
        .off("shiny:inputchanged", saveInputEvent);
}

function clearInput() {
    localStorage.removeItem("input");
}

$(document).on("shiny:connected", function() {
    loadSettings();
    loadInput();
    saveSettingsBind();
    if (localStorage.getItem("input-auto") === "true") {
        saveInputBind();
        bootstrap.Button.getOrCreateInstance($("#input-auto-btn")).toggle();
    }
})

$(function() {
    $("#input-save-btn").on("click", saveInput);
    $("#input-clear-btn").on("click", clearInput);
    $("#input-auto-btn").on("click", function(event) {
        if ($(this).hasClass("active")) {
            saveInputBind();
            localStorage.setItem("input-auto", "true");
        } else {
            saveInputUnbind();
            localStorage.setItem("input-auto", "false");
        }
    });
})

/* MathJax */
$("#MathJax-script").on("load", function() {
    MathJax.typeset();
});
