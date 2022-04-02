"use strict";

// Functions for opening book metadata pages
const bookPages = {
    statusText: "<h3 id='statusText' style='display:none;'></h3>",
    bookFields: [
        ["Title", "title"],
        ["Author", "author"],
        ["Series", "series"],
        ["ISBN", "isbn"],
        ["Publisher", "publisher"],
        ["Language", "language"],
        ["Release Date", "releaseDate"]
    ],
    errorStyle: "color: red;",
    // Create a new book
    new: function () {
        let pageTop = buttonsHTML.backSvg() + buttonsHTML.saveSvg("api.new()") + "<h1>New Book</h1>";
        api.currentBook = api.emptyBook;
        document.getElementById("detailsContainer").innerHTML = pageTop + this.bookEditHTML();
    },
    // Edit the current book
    edit: function () {
        let pageTop = buttonsHTML.backSvg("openPage(\"view\", \"" + api.currentBookID + "\")") + buttonsHTML.saveSvg("api.edit()") + "<h1>Edit Book</h1>";
        document.getElementById("detailsContainer").innerHTML = pageTop + this.bookEditHTML();
    },
    // Edit book HTML for new and edit books
    bookEditHTML: function (book) {
        // Form top
        let form = this.statusText + "<form id='bookEditForm'>";
        
        // Text book fields
        for (let field of this.bookFields.slice(0, -1)) {
            form += this.bookEditField(field[0], field[1]);
        }
        // date and end form
        form += this.bookEditField("Release Date", "releaseDate", "date") + "</form>";
        return form;
    },
    // Used by bookEditHTML to get fields of data
    bookEditField: function (label, field, type="text") {
        return "<label for='" + field + "'>" + label + ":</label><br><input type='" + type + "' id='form" + field + "' name='" + field + "' value='" + api.currentBook[field] + "' class='bookEditFormField'><br /><br />";
    },
    // Tell the user that the view book page is loading, then call api.get
    viewBookLoading: function (bookID) {
        document.getElementById("detailsContainer").innerHTML = 
            buttonsHTML.backSvg() + buttonsHTML.editSvg() + buttonsHTML.deleteSvg() + 
            "<h1>View Book</h1>" + "<h3 id='statusText'>Loading book...</h3>";
        api.get(bookID);
    },
    // Show the book to the user
    viewBookShow: function (book, status) {
        api.currentBook = book;
        let bookHTML = "";
        // Generate HTML of information
        for (let field of this.bookFields) {
            if (book[field[1]].length != 0) {
                bookHTML += "<h4 class='viewBook'>" + field[0] + ":</h4><h3 class='viewBook'>" + book[field[1]] + "</h3>";
            }
        } 
        // Add to page
        document.getElementById("detailsContainer").innerHTML = 
            buttonsHTML.backSvg() + buttonsHTML.editSvg("openPage(\"edit\", \"" + api.currentBookID + "\")") + buttonsHTML.deleteSvg("api.delete()") +
            "<h1>View Book</h1>" + this.statusText + bookHTML;
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
    // Current book being viewed
    currentBook: this.emptyBook,
    currentBookID: 0,
    // Upload a new book to the server, then open that book
    new: function () {
        this.upload("POST", "/api/new");
    },
    edit: function () {
        this.upload("PUT", "/api/edit/" + this.currentBookID);
    },
    // Create a new book or edit an existing one
    upload: function (method, url) {
        // Dont send another request if already uploading
        let uploadStatusMessage = "Uploading book..."
        let status = document.getElementById("statusText");
        if (status.innerText == uploadStatusMessage) {
            return;
        }

        // Tell user that book is being uplaoded
        status.style = "";
        status.innerText = uploadStatusMessage;

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
                    if (api.currentBookID == 0) {
                        api.currentBookID = response.bookID;
                    }
                    // Open book
                    openPage("view", api.currentBookID, false);
                }
                // Upload failed, tell user
                else {
                    api.errorMessage(req, status, "upload", book);
                }
            }
        };
        req.open(method, url);
        req.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
        req.send(JSON.stringify(book));
    },
    // Get book data then call bookPages.viewBookShow
    get: function (bookID) {
        let req = new XMLHttpRequest();
        req.onreadystatechange = function () {
            if (req.readyState == 4) {
                if (req.status == 200) {
                    bookPages.viewBookShow(JSON.parse(req.responseText), req.status);
                }
                else {
                    let status = document.getElementById("statusText");
                    api.errorMessage(req, status, "get");
                }
            }
        };
        req.open("GET", "/api/get/" + bookID);
        req.send();
    },
    // Delete a book then close the page
    delete: function () {
        // Do nothing if already deleting book
        let delStatusMessage = "Deleting book...";
        let status = document.getElementById("statusText");
        if (status.innerText == delStatusMessage) {
            return;
        }
        // Check user didnt missclick then delete book
        if (confirm("Are you sure you want to delete \"" + this.currentBook.title + "\"?")) {
            status.style = "";
            status.innerText = delStatusMessage;

            let req = new XMLHttpRequest();
            req.onreadystatechange = function () {
                if (req.readyState == 4) {
                    // Delete successful, close page
                    if (req.status == 200) {
                        openPage("none");
                    }
                    else {
                        api.errorMessage(req, status, "delete");
                    }
                }
            };
            req.open("DELETE", "/api/delete/" + this.currentBookID);
            req.send();
        }
    },
    errorMessage: function (req, element, action, book=this.emptyBook) {
        element.style = "color: red;";
        if (action == "upload" && book.title == "") {
            element.innerText = "You must enter a book title."
        }
        else if (req.status == 404) {
            element.innerText = "Error 404: Book not found.";
        }
        else if (req.status == 0) {
            element.innerText = "Error: Could not connect to the server.";
        }
        else {
            element.innerText = "Error" + req.status + ": " + req.statusText;
        }
    }
}