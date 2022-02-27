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
    if (page == "new" || page == "edit") {
        if (!confirm ("Are you sure?")) { return }
    }
    currentPage = page;
    switch (page) {
        case "settings":
            return settings.openSettingsPage();
        default:
            return;
    }
}