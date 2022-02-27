"use strict";

// Functions for changing theme and layout in the settings page
const settings = {
    // A select theme button runs this when clicked
    setTheme: function(theme) {
        this.updateBodyClass(theme, "ColorScheme");
        document.cookie = "uiTheme=" + theme + ";sameSite=Lax"; 
        this.updateButtonText(theme);
    },
    // Get all buttons and set the text to "Select" except
    // the selected button
    updateButtonText: function (theme) {
        const buttons = document.getElementsByClassName("setThemeButton");
        for (let i = 0; i < buttons.length; i++) {
            if (buttons[i].id == theme + "SetTheme") {
                buttons[i].innerText = "Selected";
            }
            else {
                buttons[i].innerText = "Select";
            }
        }
    },
    // Get the current layout/theme from the body class
    getCurrentBodyClass: function (type) {
        const classes = document.body.className.split(" ");
        for (let i = 0; i < classes.length; i++) {
            if (classes[i].endsWith(type)) {
                return classes[i].slice(0, (0 - type.length));
            }
        }
    },
    // Update the layout/theme class in the body element
    updateBodyClass: function(name, type) {
        const classes = document.body.className.split(" ");
        for (let i = 0; i < classes.length; i++) {
            if (classes[i].endsWith(type)) {
                classes[i] = name + type;
            }
        }
        document.body.className = classes.join(" ");
    },
    // Color Schemes in /static/styles/colorSchemes.css and must be added sendIndex in server.py
    colorSchemes: ["breeze", "white", "black", "nordic", "iolite"],
    // Generate the HTML for the settings page and add it to the detailsContainer div
    openSettingsPage: function() {
        var settingsHTML = "<div id='settingsContainer'>\
            <h1>Settings</h1>\
            <h2>Layout</h2>\
            <h2>Theme</h2>";

        var selectedTheme = this.getCurrentBodyClass("ColorScheme");
        for (let theme of this.colorSchemes) {
            let buttonText = "Select";
            if (theme == selectedTheme) {
                buttonText += "ed";
            }
            settingsHTML += "<div class='layoutExample " + theme + "ColorScheme'> <button onclick='settings.setTheme(\"" + theme + "\")' id='" + theme + "SetTheme' class='setThemeButton'>" + buttonText + "</button><h3>" + theme[0].toUpperCase() + theme.slice(1) + "</h3></div>";
        }
        settingsHTML += "</div>";
        document.getElementById("detailsContainer").innerHTML = settingsHTML;
    }
};