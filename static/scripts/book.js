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
    viewBookShow: function (book) {
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
};

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

        // Tell user that book is being uploaded
        status.style = "";
        status.innerText = uploadStatusMessage;

        // Get book data from form
        const book = {};
        const fields = document.getElementsByClassName("bookEditFormField");
        for (let field of fields) {
            book[field.name] = field.value
        }

        // Upload book to the server
        this.request(method, url, "upload", function (req) {
            let response = JSON.parse(req.responseText);
            // Get book ID if new book
            if (api.currentBookID == 0) {
                api.currentBookID = response.bookID;
            }
            // Open book
            openPage("view", api.currentBookID, false);
            search.search(false);
        }, book);
    },
    // Get book data then call bookPages.viewBookShow
    get: function (bookID) {
        this.request("GET", "api/get/" + bookID, "get", function (req) {
            bookPages.viewBookShow(JSON.parse(req.responseText));
        });
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

            this.request("DELETE", "api/delete/" + this.currentBookID, "delete", function () {
                openPage("none");
                search.search(false);
            });
        }
    },
    // XMLHttpRequest for get, upload, and delete
    request: function (method, url, action, onSuccess, data=null) {
        let req = new XMLHttpRequest();
        req.onreadystatechange = function () {
            if (req.readyState == 4) {
                if (req.status == 200) {
                    onSuccess(req);
                }
                else {
                    api.errorMessage(req, action, data);
                }
            }
        };
        req.open(method, url);
        // Only sent json if there is data to send.
        if (data == null) {
            req.send();
        }
        else {
            req.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
            req.send(JSON.stringify(data));
        }
    },
    // User understandable error messages
    errorMessage: function (req, action, book={}) {
        if (action == "search") {
            var status = document.getElementById("bookListStatusText");
        }
        else {
            var status = document.getElementById("statusText");
        }
        status.style = "color: red;";
        if (action == "upload" && book.title == "") {
            status.innerText = "You must enter a book title.";
        }
        else if (req.status == 404) {
            status.innerText = "Error 404: Book not found.";
        }
        else if (req.status == 0) {
            status.innerText = "Error: Could not connect to the server.";
        }
        else {
            status.innerText = "Error " + req.status + ": " + req.statusText;
        }
    }
};

// Search related functions
const search = {
    // Search button or DOMContentLoaded
    search: function (tellUser=true) {
        if (tellUser) {
            document.getElementById("bookList").innerHTML = "<h3 id='bookListStatusText'>Loading books...</h3>";
        }
        let query = document.getElementById("controlsSearchText").value;
        api.request("GET", "api/search?q=" + query, "search", function (req) {
            search.showResults(JSON.parse(req.responseText));
        });
    },
    headerFields: ["Cover", "Title", "Author"],
    tableCell: function (field, text="", tagName="td") {
        let cell = document.createElement(tagName);
        cell.className = field;
        let p = document.createElement("p");
        p.innerText = text;
        cell.appendChild(p);
        return cell;
    },
    // Called by api.search, generate the HTML for the search results
    showResults: function (response) {
        let fragment = document.createDocumentFragment();
        // Generate table
        let table = document.createElement("table");
        table.id = "bookList";
        let tableHeader = document.createElement("tr");
        for (let field of this.headerFields) {
            tableHeader.appendChild(this.tableCell(field, field, "th"));
        }
        table.appendChild(tableHeader);
        for (let book of response.books) {
            let row = document.createElement("tr");
            row.onclick = this.bookSelected;
            row.id = book.bookID;

            let img = this.tableCell("Cover");
            img.innerHTML = "<img src = /book/cover/" + book.bookID + "/preview>";
            row.appendChild(img);

            for (let field of this.headerFields.slice(1)) {
                row.appendChild(this.tableCell(field, book[field.toLowerCase()]));
            }
            table.appendChild(row);
        }
        fragment.appendChild(table);

        // Information about search
        let info = document.createElement("p");
        info.id = "searchInfo";
        info.innerText = "Showing ";
        let length = Object.keys(response.books).length;
        if (length < response.total) {
            info.innerText += response.first + " to " + response.last + " of ";
        }
        info.innerText += response.total + " books (" + response.time + "ms)";
        fragment.appendChild(info);

        document.getElementById("listContainer").replaceChildren(fragment);
        editClassifExists(api.currentBookID, "selectedBook");
    },
    // Open a book when it is selected, do nothing if already open
    bookSelected: function (event) {
        if (document.getElementById(this.id).className == "") {
            openPage("view", this.id);
        }
    }
};

// Empty search on page load
document.addEventListener("DOMContentLoaded", search.search());

document.getElementById("controlsSearchText").addEventListener("keyup", function (event) {
    if (event.key === "Enter") {
        search.search();
    }
});