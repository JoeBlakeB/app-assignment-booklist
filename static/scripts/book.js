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
            this.bookEditField("Title", book.title, "title") + 
            this.bookEditField("Author", book.author, "author") + 
            this.bookEditField("Series", book.series, "series") + 
            this.bookEditField("ISBN", book.isbn, "isbn") + 
            this.bookEditField("Release Date", book.releaseDate, "releaseDate", "date") + 
            this.bookEditField("Publisher", book.publisher, "publisher") +
            this.bookEditField("Language", book.language, "language") +
            "</form>";
    },
    // Used by bookEditHTML to get fields of data
    bookEditField: function (label, value, name, type="text") {
        return "<label for='form" + label + "'>" + label + ":</label><br><input type='" + type + "' id='form" + label + "' name='" + name + "' value='" + value + "' class='bookEditFormField'><br /><br />";
    }
}

// API related functions
const api = {
    // Empty book object
    emptyBook: {
        "title": "",
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
    new: function () {
        this.upload("POST", "/api/new");
    },
    // Create a new book or edit an existing one
    upload: function (method, url) {
        // Dont send another request if already uploading
        let status = document.getElementById("statusText");
        if (status.innerText == "Uploading book...") {
            return;
        }

        // Tell user that book is being uplaoded
        status.style = "";
        status.innerText = "Uploading book...";

        // Get book data from form
        const book = {};
        const fields = document.getElementsByClassName("bookEditFormField");
        for (let field of fields) {
            book[field.name] = field.value
        }

        // Upload book to the server
        let req = new XMLHttpRequest();
        req.onreadystatechange = function () {
            if (req.readyState == 4) {
                // Upload successful
                if (req.status == 200) {
                    let response = JSON.parse(req.responseText);
                    // Get book ID if new book
                    if (currentBookID == 0) {
                        currentBookID = response.currentBookID;
                    }
                    // Open book
                    openPage("view", currentBookID, false);
                }
                // Upload failed, tell user
                else {
                    status.style = "color: red;";
                    if (book.title == "") {
                        status.innerText = "You must enter a book title."
                    }
                    else if (req.status == 0) {
                        status.innerText = "Error: Could not connect to the server.";
                    }
                    else {
                        status.innerText = "Error: Could not upload book to the server.";
                    }
                }
            }
        };
        req.open(method, url);
        req.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
        req.send(JSON.stringify(book));
    }
}