"use strict";

// Functions for generating and using the book pages
const bookPages = {
    statusText: "<h3 id='statusText' style='display:none;'></h3>",
    bookFields: [
        ["Title", "title"],
        ["Author", "author"],
        ["Series", "series"],
        ["Genre", "genre"],
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
        form += this.bookEditField("Release Date", "releaseDate", "date");
        
        form += "<label for='formCover'>Book Cover Image:</label><div ondragover='bookPages.coverDrop(event)' ondrop='bookPages.coverDrop(event)' id='coverUploadDiv'><div id='coverUploadInput'><input type='file' id='formCover' name='cover' accept='image/*' onchange='bookPages.coverChange(true)'><p id='formCoverFilename'></p><p onclick='bookPages.coverChange(false)' id='formCoverDelete'>"
        if (api.currentBook.hasCover) {
            form += "Remove Current Cover"
        }
        api.bookCoverAction = null;
        form += "</p></div><div id='bookCoverPreview'>" + this.coverPreview() + "</div></div><label for='formFiles'>Book Files:</label>" + this.fileTableHTML("edit") + "</form>";
        return form;
    },
    // Allow drag and drop into the entire book cover div
    coverDrop: function (event) {
        event.preventDefault();
        if (event.dataTransfer.files.length) {
            let fileInput = document.getElementById("formCover");
            fileInput.files = event.dataTransfer.files;
            this.coverChange(true);
        }
    },
    // Generates html for book cover preview images
    coverPreview: function (newFile = undefined) {
        let currentImg = "";
        let newImg = "";
        if (api.currentBook.hasCover) {
            currentImg = "<div><p>Current:</p><img id='coverCurrentPreview' src='/book/cover/" + api.currentBookID + "?lastmodified=" + api.currentBook.lastModified + "'></div>";
        }
        if (api.bookCoverAction == "upload") {
            newImg = "<div><p>New:</p><img id='coverUploadPreview' src='" + URL.createObjectURL(newFile) + "'></div>";
        }
        else if (api.bookCoverAction == "delete") {
            newImg = "<div><p>New:</p><img id='coverUploadPreview' src='/static/images/bookCoverPlaceholder.png'></div>";
        }

        return currentImg + newImg;
    }, 
    // Called when a file is selected or when the remove text is clicked
    coverChange: function (newFile) {
        let fileInput = document.getElementById("formCover");
        let fileName = document.getElementById("formCoverFilename");
        let deleteText = document.getElementById("formCoverDelete");
        // Reset input
        if (!newFile) {
            fileName.innerText = "";
            fileInput.value = null;
        }
        // Set cover delete text and set action
        if (newFile) {
            fileName.innerText = fileInput.files[0].name;
            deleteText.innerText = "Reset";
            api.bookCoverAction = "upload";
        }
        else if (api.bookCoverAction == "delete" || 
            (api.bookCoverAction == "upload" && api.currentBook.hasCover)) {
            deleteText.innerText = "Remove Current Cover";
            api.bookCoverAction = null;
        }
        else if (api.bookCoverAction == "upload") {
            deleteText.innerText = "";
            api.bookCoverAction = null;
        }
        else {
            deleteText.innerText = "Reset";
            api.bookCoverAction = "delete";
        }
        // Generate new html for images
        document.getElementById("bookCoverPreview").innerHTML = this.coverPreview(fileInput.files[0]);
    },
    // Used by bookEditHTML to get fields of data
    bookEditField: function (label, field, type = "text") {
        return "<label for='form" + field + "'>" + label + ":</label><input type='" + type + "' id='form" + field + "' name='" + field + "' value='" + api.currentBook[field] + "' class='bookEditFormField bookEditFormInput'>";
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
            if (book[field[1]] != "" && book[field[1]]) {
                bookHTML += "<h4 class='viewBook'>" + field[0] + ":</h4><h3 class='viewBook'>" + book[field[1]] + "</h3>";
            }
        } 
        bookHTML += "</div>";
        // Book Cover
        if (book.hasCover) {
            bookHTML += "<div class='viewBookDivider coverDivider'><img class='viewCover' src='/book/cover/" + api.currentBookID + "?lastmodified=" + book.lastModified + "' ></div>";
        }
        // Add to page
        document.getElementById("detailsContainer").innerHTML = "<div class='flexContainer'><div class='viewBookDivider bookMetadata'>" + 
            buttonsHTML.backSvg() + buttonsHTML.editSvg("openPage(\"edit\", \"" + api.currentBookID + "\")") + buttonsHTML.deleteSvg("api.delete()") +
            "<h1>View Book</h1>" + this.statusText + bookHTML + "</div>" + this.fileTableHTML("view");
    },
    // Generate the file table html
    fileTableHTML: function (page) {
        let fileTable = "<table id='" + page + "FileTable' class='fileTable' ondragover='bookPages.fileDrop(event)' ondrop='bookPages.fileDrop(event)'>";
        // Upload file button
        if (page == "edit") {
            api.bookFilesNew = { index: 1 };
            api.bookFilesDelete = [];
            fileTable += "<td colspan='3'><input type='file' id='formFiles' name='files' onchange='bookPages.addFiles()' multiple><p id='fileUploadStats'></p></td>";
        }
        // Return if view and no files
        else if (api.currentBook.files.length == 0) {
            return "";
        }
        // Row for each file
        for (let file of api.currentBook.files) {
            fileTable += this.fileRowHTML(file.hashName, file.name, page, "/static/svg/pdf.svg", file.size);
        }
        return fileTable + "</table>";
    },
    // Generate a row for the file table
    fileRowHTML: function (fileID, fileName, type, image, fileSize=0) {
        let fileTable = "<tr class='fileTableRow' id='" + fileID + "'><td><img class='fileIcon' src='" + image + "'></td>";
        if (type == "view") {
            fileTable += "<td class='fileName'><p>" + fileName + " (" + api.fileSize(fileSize) + ")</p></td><td>" + buttonsHTML.downloadSvg("window.open(\"/book/file/" + api.currentBookID + "/" + fileID + "\")");
        }
        else {
            fileTable += "<td class='fileName'><input type='text' class='bookEditFormInput' id='fileNameInput-" + fileID + "' value='" + fileName + "'></td><td>";
            if (type == "edit") {
                fileTable += buttonsHTML.deleteSvg("bookPages.deleteFileButton(\"" + fileID + "\")");
            }
            else {
                fileTable += type;
            }
        }
        return fileTable + "</td></tr>";
    },
    // Allow drag and drop into the entire book files table
    fileDrop: function (event) {
        event.preventDefault();
        if (event.dataTransfer.files.length) {
            this.addFiles(Array.from(event.dataTransfer.files));
        }
    },
    // A file has been added, add it to the table
    addFiles: function (files=null) {
        // Files were added via the button, not drag and drop
        if (!files) {
            let fileInput = document.getElementById("formFiles");
            files = Array.from(fileInput.files);
            fileInput.value = null;
        }
        // Add them to the HTML
        let table = document.getElementById("editFileTable").firstChild;
        for (let file of files) {
            let fileID = "newFile" + api.bookFilesNew.index++;
            table.innerHTML += this.fileRowHTML(fileID, file.name, buttonsHTML.cancelSvg("bookPages.cancelUploadButton(\"" + fileID + "\")"), "/static/svg/new.svg");
            api.bookFilesNew[fileID] = file;
        }
    },
    // Remove a new file from the table and api.bookFilesNew
    cancelUploadButton: function (fileID) {
        delete api.bookFilesNew[fileID];
        document.getElementById(fileID).remove();
    },
    // Add file to api.bookFilesDelete and update the table
    deleteFileButton: function (fileID) {
        api.bookFilesDelete.push(fileID);
        let element = document.getElementById(fileID);
        element.children[0].firstChild.src = "/static/svg/delete.svg";
        element.children[1].firstChild.disabled = true;
        element.children[1].firstChild.value = api.fileFromHashName(fileID).name;
        element.children[2].innerHTML = buttonsHTML.undoSvg("bookPages.restoreFileButton(\"" + fileID + "\")");
    },
    // Remove a file from api.bookFilesDelete and update the table
    restoreFileButton: function (fileID) {
        let element = document.getElementById(fileID);
        element.children[0].firstChild.src = "/static/svg/pdf.svg";
        element.children[1].firstChild.disabled = false;
        element.children[2].innerHTML = buttonsHTML.deleteSvg("bookPages.deleteFileButton(\"" + fileID + "\")");
        let arrayIndex = api.bookFilesDelete.indexOf(fileID);
        api.bookFilesDelete.splice(arrayIndex, 1);
    }
};

// API related functions
const api = {
    // Empty book object
    emptyBook: {
        "title": "",
        "author": "",
        "series": "",
        "genre": "",
        "isbn": "",
        "releaseDate": "",
        "publisher": "",
        "language": "",
        "files": [],
        "hasCover": false,
        "lastModified": 0
    },
    // Current book being viewed
    currentBook: this.emptyBook,
    currentBookID: 0,
    requestsCount: 0,
    bookCoverAction: null,
    bookFilesNew: {},
    bookFilesDelete: [],
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
        let uploadStatusMessage = "Uploading book...";
        let status = document.getElementById("statusText");
        if (status.style.length == 0) {
            return;
        }

        // Tell user that book is being uploaded
        status.style = "";
        status.innerText = uploadStatusMessage;

        // Get book data from form
        const book = {};
        const fields = document.getElementsByClassName("bookEditFormField");
        for (let field of fields) {
            book[field.name] = field.value;
        }

        // Upload book to the server
        this.request(method, url, "upload", function (req) {
            let response = JSON.parse(req.responseText);
            // Get book ID if new book
            if (api.currentBookID == 0) {
                api.currentBookID = response.bookID;
            }
            // Upload Files
            api.requestsCount = api.uploadFiles();
            // Open book if no other requests
            api.openPageIfDone();
        }, JSON.stringify(book), "application/json;charset=UTF-8");
    },
    // Go back to view only when all requests are complete
    openPageIfDone: function () {
        if (--api.requestsCount <= 0) {
            openPage("view", api.currentBookID, false);
            search.search(search.currentPage, false);
        }
    },
    // Send the requests for uploading and deleting files and covers
    uploadFiles: function () {
        let requestsCount = 0;
        // Book cover
        if (api.bookCoverAction == "upload") {
            let coverFile = document.getElementById("formCover").files[0];
            this.request("PUT", "/api/cover/" + api.currentBookID + "/upload", "upload", function (req) {
                api.openPageIfDone();
            }, coverFile, coverFile.type);
            requestsCount++;
        }
        else if (api.bookCoverAction == "delete") {
            this.request("DELETE", "/api/cover/" + api.currentBookID + "/delete", "delete", function (req) {
                api.openPageIfDone();
            });
            requestsCount++;
        }
        // File uploads
        for (let fileID of Object.keys(api.bookFilesNew).splice(1)) {
            let file = api.bookFilesNew[fileID];
            let fileNameInput = document.getElementById("fileNameInput-" + fileID);
            let fileName = fileNameInput.value;
            let fileExtention = "." + file.name.split(".").slice(-1);
            if (!fileName.endsWith(fileExtention)) {
                fileName += fileExtention
            }
            this.request("POST", "/api/file/upload/" + api.currentBookID + "/" + fileName, "upload", function (req) {
                api.openPageIfDone();
            }, file, file.type);
            requestsCount++;
        }
        // File deletes
        console.log(api.bookFilesDelete);
        for (let hashName of api.bookFilesDelete) {
            this.request("DELETE", "/api/file/delete/" + api.currentBookID + "/" + hashName, "delete", function (req) {
                api.openPageIfDone();
            });
            requestsCount++;
        }
        // File renames
        let fileRenames = {};
        for (let file of api.currentBook.files) {
            if (!api.bookFilesDelete.includes(file.hashName)) {
                let fileNameInput = document.getElementById("fileNameInput-" + file.hashName);
                if (fileNameInput.value != file.name && fileNameInput.value.length) {
                    fileRenames[file.hashName] = fileNameInput.value;
                }
            }
        }
        fileRenames = JSON.stringify(fileRenames)
        if (fileRenames != "{}") {
            this.request("POST", "/api/file/rename/" + api.currentBookID, "fileRename", function (req) {
                api.openPageIfDone();
            }, fileRenames, "application/json;charset=UTF-8");
            requestsCount++;
        }
        // Return the number of requets being done
        return requestsCount;
    },
    // Get full file from hashName of currentBook
    fileFromHashName: function (hashName) {
        for (let book of this.currentBook.files) {
            if (book.hashName == hashName) {
                return book
            }
        }
        return null;
    },
    // Get book data then call bookPages.viewBookShow
    get: function (bookID) {
        this.request("GET", "api/get/" + bookID, "get", function (req) {
            let book = JSON.parse(req.responseText);
            book.files = book.files.splice(1);
            bookPages.viewBookShow(book);
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
                search.search(search.currentPage, false);
            });
        }
    },
    // XMLHttpRequest for get, upload, and delete
    request: function (method, url, action, onSuccess, data=null, contentType=null) {
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
            req.setRequestHeader("Content-Type", contentType);
            req.send(data);
        }
    },
    // User understandable error messages
    errorMessage: function (req, action, book={}) {
        if (action == "search") {
            let bookList = document.getElementById("listContainer");
            bookList.innerHTML = "<h3 id='bookListStatusText'>Loading books...</h3>";
            var status = bookList.firstChild;
        }
        else {
            var status = document.getElementById("statusText");
        }
        status.style = "color: red;";
        if (action == "upload" && book.title == undefined) {
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
    },
    fileSize: function (size) {
        let units = ["Bytes", "KB", "MB", "GB"];
        let unit = 0;
        while (size > 1024 && unit < units.length) {
            unit ++;
            size /= 1024;
        }
        return Math.round(size) + " " + units[unit];
    }
};

// Search related functions
const search = {
    currentPage: 0,
    lastPage: 1,
    booksPerPage: 25,
    // Search button or DOMContentLoaded
    search: function (page=0, tellUser=true) {
        if (tellUser) {
            document.getElementById("listContainer").innerHTML = "<h3 id='bookListStatusText'>Loading books...</h3>";
        }
        if (typeof page === "object") {
            page = 0
        }
        search.currentPage = page;
        let offset = search.booksPerPage * page;
        let query = document.getElementById("controlsSearchText").value;
        api.request("GET", "api/search?q=" + query + "&limit=" + search.booksPerPage + "&offset=" + offset, "search", function (req) {
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
            if (book.hasCover) {
                img.innerHTML = "<img src = '/book/cover/" + book.bookID + "/preview?lastModified=" + book.lastModified + "' >";
            }
            else {
                img.innerHTML = "<img src = '/static/images/bookCoverPlaceholderPreview.png' >";
            }
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
        let length = Object.keys(response.books).length;
        if (length > 0) {
            info.innerText = "Showing ";
            if (length < response.total) {
                info.innerText += response.first + " to " + response.last + " of ";
            }
            info.innerText += response.total + " books"
        }
        else {
            info.innerText = "Your search did not match any books."
        }
        info.innerText += " (" + response.time + "ms)";
        fragment.appendChild(info);

        // Page selector
        if (length < response.total) {
            fragment.appendChild(this.pageSelector(response.total));
        }

        document.getElementById("listContainer").replaceChildren(fragment);
        editClassifExists(api.currentBookID, "selectedBook");
    },
    // Generate the page selector for the bottom of the book list
    pageSelector: function (total) {
        let menu = document.createElement("menu");
        menu.id = "pageSelector";
        let currentPage = this.currentPage + 1;
        this.lastPage = Math.ceil(total / this.booksPerPage);
        let pageButtons = 5;

        menu.appendChild(this.pageButton("<"));
        // Before current page
        let start = 1;
        let extraBefore = currentPage - (this.lastPage - pageButtons);
        if (extraBefore < 0) { extraBefore = 0; }
        if (currentPage > pageButtons + 1 + extraBefore) {
            menu.appendChild(this.pageButton(1));
            menu.appendChild(this.pageButton("···", false, "searchPageSeperator"));
            start = currentPage - (pageButtons - 2 + extraBefore);
        }
        for (let i = start; i < currentPage && i < this.lastPage; i++) {
            menu.appendChild(this.pageButton(i));
        }
        // Current page
        menu.appendChild(this.pageButton(currentPage, true, "searchPageSelected"));
        // After current page
        let extraAfter = pageButtons + 1 - currentPage;
        if (extraAfter < 0) { extraAfter = 0; }
        if (this.lastPage - currentPage > pageButtons + extraAfter) {
            for (let i = currentPage + 1; i <= currentPage + pageButtons - 2 + extraAfter; i++) {
                menu.appendChild(this.pageButton(i));
            }
            menu.appendChild(this.pageButton("···", false, "searchPageSeperator"));
            menu.appendChild(this.pageButton(this.lastPage));
        }
        else {
            for (let i = currentPage + 1; i <= this.lastPage; i++) {
                menu.appendChild(this.pageButton(i));
            }
        }
        menu.appendChild(this.pageButton(">"));

        return menu;
    },
    // Used to generate each button for the page selector menu
    pageButton: function (pageNumber, clickable=true, className="searchPageOption") {
        let li = document.createElement("li");
        li.className = className;
        if (clickable) {
            li.onclick = search.pageButtonClicked;
        }
        let span = document.createElement("span");
        span.innerText = pageNumber;
        li.appendChild(span);
        return li;
    },
    pageButtonClicked: function () {
        let text = this.firstChild.innerText;
        if (!Number.isNaN(Number(text))) {
            search.search(Number(text) - 1, false);
        }
        else if (text == "<") {
            let last = search.currentPage - 1;
            if (last < 0) { last = 0; }
            search.search(last, false);
        }
        else if (text == ">") {
            let next = search.currentPage + 1;
            if (next >= search.lastPage) { next = search.currentPage; }
            search.search(next, false);
        }
    },
    // Open a book when it is selected, do nothing if already open
    bookSelected: function () {
        if (this.className == "") {
            openPage("view", this.id);
        }
    }
};

// Empty search on page load
document.addEventListener("DOMContentLoaded", search.search);

document.getElementById("controlsSearchText").addEventListener("keyup", function (event) {
    if (event.key === "Enter") {
        search.search();
    }
});