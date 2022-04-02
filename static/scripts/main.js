"use strict";

var currentPage = "none";

// Will return if the page is already open
// If the page is edit or new book, will ask user to confirm
// before changing page
// Will then run the corresponding function for the page
//
// Parameters:
// page        the page that should be opened
// bookID      the book to open (optional, 0 if not a book)
// showWarning show a warning if leaving page new or edit (optional, true by default)
function openPage(page, bookID=0, showWarning=true) {
    if (page == currentPage && page != "view") { return }
    if ((currentPage == "new" || currentPage == "edit") && showWarning) {
        if (!confirm ("Are you sure you want to leave without saving?")) { return }
    }
    currentPage = page;
    api.currentBookID = bookID;
    showDetailsContainer(page != "none");
    switch (page) {
        case "none":
            return document.getElementById("detailsContainer").innerHTML = "";
        case "settings":
            return settings.openSettingsPage();
        case "view":
            return bookPages.viewBookLoading(bookID);
        case "edit":
            return bookPages.edit();
        case "new":
            return bookPages.new();
        default:
            return;
    }
}

// Add the showDetailsContainer class to body so that only one
// container is displayed on mobile mode
function showDetailsContainer(addClass) {
    // Return if nothing needs to be added/removed
    var alreadyAdded = document.body.className.includes("showDetailsContainer");
    if ((addClass && alreadyAdded) || (!addClass && !alreadyAdded)) { return }
    // Add showDetailsContainer to body classes
    else if (addClass) {
        document.body.className = document.body.className + " showDetailsContainer";
    }
    // Remove showDetailsContainer from the body class
    else {
        document.body.classList.remove("showDetailsContainer");
    }
}

// HTML for buttons used in multiple different places
const buttonsHTML = {
    backSvg: function (onclick="openPage(\"none\")") {
        return "<button id='backButton' class='controlsButton' onclick='" + onclick + "'> <svg height='24' width='24' transform='scale(1.25)'> <path d='m 11.000024,4 c 0.554,0 1,0.446 1,1 V 9 H 20 c 0.554,0 1,0.446 1,1 v 3 c 0,0.554 -0.446,1 -1,1 h -7.999977 v 4 c 0,0.554 -0.445999,1 -1,1 -0.298584,0 -0.565122,-0.129747 -0.748046,-0.335938 L 3.273438,12.185547 C 3.104355,12.006452 3,11.76574 3,11.5 3,11.23426 3.104355,10.993548 3.273438,10.814453 L 10.251977,4.3359375 C 10.434902,4.129747 10.70144,4 11.000024,4 Z' /></svg></button>"
    },
    saveSvg: function (onclick) {
        return "<button id='saveButton' class='controlsButton' onclick='" + onclick + "'> <svg height='24' width='24' transform='scale(1.75)'> <path d='m 18,19 c 0.55,0 1,-0.45 1,-1 V 7 L 17,5 H 6 C 5.45,5 5,5.45 5,6 v 12 c 0,0.55 0.45,1 1,1 z M 17,17 H 7 V 7 h 1 v 5 h 8 V 7 h 1 z M 12,11 H 10 V 7 h 2 z'/></svg></button>"
    },
    editSvg: function (onclick) {
        return "<button id='editButton' class='controlsButton' onclick='" + onclick + "'> <svg height='24' width='24' transform='scale(1.6)'> <path d='M 12.778, 1.2222 C 12.778, 1.2222 12.278, 0.72224 11.778, 1.2222 L 10, 3 13, 6 14.778, 4.2222 C 15.278, 3.7222 14.778, 3.2222 14.778, 3.2222 Z M 9, 4 1, 12 V 15 H 4 L 12, 7 Z'/></svg></button>"
    },
    deleteSvg: function (onclick) {
        return "<button id='deleteButton' class='controlsButton' onclick='" + onclick + "'> <svg height='24' width='24' transform='scale(1.5)'> <path d='M 10,4 C 9,4 9,5 9,5 H 6 C 6,5 5,5 5,6 V 7 H 19 V 6 C 19,5 18,5 18,5 H 15 C 15,5 15,4 14,4 Z M 6,8 V 19 C 6,19.52 6.48,20 7,20 H 17 C 17.52,20 18,19.52 18,19 V 8 Z'/></svg></button>"
    }
}

// Functions for changing theme and layout in the settings page
const settings = {
    // A select layout button runs this when clicked
    setLayout: function (layout) {
        this.updateBodyClass(layout, "Layout");
        document.cookie = "uiLayout=" + layout + ";sameSite=Lax";
    },
    // A select theme button runs this when clicked
    setTheme: function (theme) {
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
    updateBodyClass: function (name, type) {
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
    openSettingsPage: function () {
        var settingsHTML = "<div id='settingsContainer'>" +
            buttonsHTML.backSvg() +
            "<h1>Settings</h1>\
            <h2>Layout</h2>\
            <button onclick='settings.setLayout(\"desktop\")' class='setLayoutButton'> <svg width='64' height='64' transform='scale(3.2)' alt='Desktop Layout'> <rect style='opacity:0.2' width='32' height='42' x='16' y='14' rx='2.5' ry='2.5' /> <rect style='fill:#8e8e8e' width='32' height='42' x='16' y='13' rx='2.5' ry='2.5' /> <rect style='opacity:0.2' width='52' height='40' x='6' y='10' rx='2.5' ry='2.5' /> <path style='fill:#595959' d='M 6 44 L 6 46.5 C 6 47.885 7.115 49 8.5 49 L 55.5 49 C 56.885 49 58 47.885 58 46.5 L 58 44 L 6 44 z' /> <path style='fill:#333333' d='M 8.5,9 C 7.115,9 6,10.115 6,11.5 V 44 H 58 V 11.5 C 58,10.115 56.885,9 55.5,9 Z' /> <rect style='opacity:0.1;fill:#ffffff' width='52' height='1' x='6' y='44' /> <path style='fill:#ffffff;opacity:0.1' d='M 8.5 9 C 7.115 9 6 10.115 6 11.5 L 6 12.5 C 6 11.115 7.115 10 8.5 10 L 55.5 10 C 56.885 10 58 11.115 58 12.5 L 58 11.5 C 58 10.115 56.885 9 55.5 9 L 8.5 9 z' /> </svg> </button> \
            <button onclick='settings.setLayout(\"mobile\")' class='setLayoutButton'> <svg width='64' height='64' transform='scale(2.8)' alt='Mobile Layout'> <rect style='opacity:0.2' width='40' height='60' x='12' y='3' rx='3' ry='3' /> <path style='fill:#595959' d='M 15 2 C 13.338 2 12 3.338 12 5 L 12 8 L 52 8 L 52 5 C 52 3.338 50.662 2 49 2 L 15 2 z M 12 54 L 12 59 C 12 60.662 13.338 62 15 62 L 49 62 C 50.662 62 52 60.662 52 59 L 52 54 L 12 54 z' /> <rect style='fill:#333333' width='40' height='46' x='12' y='8' /> <path style='fill:#333333' d='M 28.25 4 C 27.5575 4 27 4.446 27 5 C 27 5.554 27.5575 6 28.25 6 L 35.75 6 C 36.4425 6 37 5.554 37 5 C 37 4.446 36.4425 4 35.75 4 L 28.25 4 z M 40 4 A 1 1 0 0 0 39 5 A 1 1 0 0 0 40 6 A 1 1 0 0 0 41 5 A 1 1 0 0 0 40 4 z M 30.5 55 C 29.669 55 29 55.669 29 56.5 L 29 59.5 C 29 60.331 29.669 61 30.5 61 L 33.5 61 C 34.331 61 35 60.331 35 59.5 L 35 56.5 C 35 55.669 34.331 55 33.5 55 L 30.5 55 z M 19.5 56 C 18.669 56 18 56.669 18 57.5 C 18 58.331 18.669 59 19.5 59 L 22.5 59 C 23.331 59 24 58.331 24 57.5 C 24 56.669 23.331 56 22.5 56 L 19.5 56 z M 41.5 56 C 40.669 56 40 56.669 40 57.5 C 40 58.331 40.669 59 41.5 59 L 44.5 59 C 45.331 59 46 58.331 46 57.5 C 46 56.669 45.331 56 44.5 56 L 41.5 56 z' /> <path style='fill:#ffffff;opacity:0.1' d='M 15 2 C 13.338 2 12 3.338 12 5 L 12 6 C 12 4.338 13.338 3 15 3 L 49 3 C 50.662 3 52 4.338 52 6 L 52 5 C 52 3.338 50.662 2 49 2 L 15 2 z' /> <rect style='opacity:0.2' width='40' height='1' x='12' y='8' /> </svg> </button> \
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