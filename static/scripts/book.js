"use strict";

// Functions for opening book metadata pages
const bookPages = {
    // Create a new book
    new: function () {
        let pageTop = buttonsHTML.backSvg + buttonsHTML.saveSvg.replace("onclick=''", "onclick='api.new()'") + "<h1>New Book</h1>";
        let pageHTML = pageTop + this.bookEditHTML(api.emptyBook);
        document.getElementById("detailsContainer").innerHTML = pageHTML;
    },
    // Edit the current book
    edit: function () {
        let pageTop = buttonsHTML.backSvg.replace("openPage(\"none\")", "openPage(\"view\")") + "<h1>Edit Book</h1>";
        let pageHTML = pageTop + this.bookEditHTML(currentBook);
        document.getElementById("detailsContainer").innerHTML = pageHTML;
    },
    // Edit book HTML for new and edit books
    bookEditHTML: function (book) {
        return "<form id='bookEditForm'>" + 
            "<h3 id='statusText' style='display:none;'></h3>" + 
            this.bookEditField("Title", book.name) + 
            this.bookEditField("Author", book.author) + 
            this.bookEditField("Series", book.series) + 
            this.bookEditField("ISBN", book.isbn) + 
            this.bookEditField("Release Date", book.releaseDate, "date") + 
            this.bookEditField("Publisher", book.publisher) +
            this.bookEditField("Language", book.language) +
            "</form>";
    },
    // Used by bookEditHTML to get fields of data
    bookEditField: function (label, value, type="text") {
        return "<label for='form" + label + "'>" + label + ":</label><br><input type='" + type + "' id='form" + label + "' name='form" + label + "' value='" + value + "'><br /><br />";
    }
}

// API related functions
const api = {
    // Empty book object
    emptyBook: {
        "name": "",
        "author": "",
        "series": "",
        "isbn": "",
        "releaseDate": "",
        "publisher": "",
        "language": "",
        "files": [],
        "hasCover": false
    },
    // Upload a new book to the server, then open that book
    new: function() {
        let status = document.getElementById("statusText");
        status.style = "";
        status.innerText = "Uploading book...";
    }
}