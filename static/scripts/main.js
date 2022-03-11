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

const buttonsHTML = {
    backSvg: "<button id='backButton' class='controlsButton' onclick='openPage(\"none\")'>\
    <svg height='24' width='24' transform='scale(1.25)'>\
    <path d='m 11.000024,4 c 0.554,0 1,0.446 1,1 V 9 H 20 c 0.554,0 1,0.446 1,1 v 3 c 0,0.554 -0.446,1 -1,1 h -7.999977 v 4 c 0,0.554 -0.445999,1 -1,1 -0.298584,0 -0.565122,-0.129747 -0.748046,-0.335938 L 3.273438,12.185547 C 3.104355,12.006452 3,11.76574 3,11.5 3,11.23426 3.104355,10.993548 3.273438,10.814453 L 10.251977,4.3359375 C 10.434902,4.129747 10.70144,4 11.000024,4 Z' />\
    </svg></button>"
}