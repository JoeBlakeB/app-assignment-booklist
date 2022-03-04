"use strict";

var currentPage = "none";

// Will return if the page is already open
// If the page is edit or new book, will ask user to confirm
// before changing page
// Will then run the corresponding function for the page
// param    page    the page that should be opened
// param    isbn    the book to open (optional, 0 if not a book)
function openPage(page, isbn=0) {
    if (page == currentPage) { return }
    if (currentPage == "new" || currentPage == "edit") {
        if (!confirm ("Are you sure?")) { return }
    }
    currentPage = page;
    showDetailsContainer(page != "none");
    switch (page) {
        case "none":
            return document.getElementById("detailsContainer").innerHTML = "";
        case "settings":
            return settings.openSettingsPage();
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