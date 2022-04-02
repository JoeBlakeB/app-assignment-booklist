#!/usr/bin/env python3

import flask
import os
import sys
import time

from database import database

booklist = flask.Flask(__name__, template_folder=".")
booklist.config["TEMPLATES_AUTO_RELOAD"] = True
booklist.url_map.strict_slashes = False

@booklist.after_request
def afterRequest(response):
    """Add server to user agent"""
    response.headers["Server"] = f"AppAssignmentBooklist Python/{sys.version.split()[0]}"
    return response


@booklist.route("/")
def sendIndex():
    """Send the booklist page with body classes added based on cookies and user agent."""
    userAgent = flask.request.headers.get('User-Agent').lower()
    if ("phone" in userAgent or "android" in userAgent) or (
            "mobile" in str(flask.request.cookies.get("uiLayout"))):
        bodyClasses = "mobileLayout"
    else:
        bodyClasses = "desktopLayout"

    uiTheme = flask.request.cookies.get("uiTheme")
    # Themes are kept in /static/styles/colorScheme.css
    if uiTheme in ["breeze", "white", "black", "nordic", "iolite"]:
        bodyClasses += " " + uiTheme + "ColorScheme"
    else:
        bodyClasses += " breezeColorScheme"

    return flask.render_template("index.html", bodyClasses=bodyClasses)


@booklist.route("/static/<path:path>")
def sendStatic(path):
    """Send all files in the static folder"""
    return flask.send_from_directory("static", path)


@booklist.route("/book/cover/<bookID>", defaults={"size": ""})
@booklist.route("/book/cover/<bookID>/preview", defaults={"size": "Preview"})
def bookCover(bookID, size):
    """Sends the cover of a book"""
    if db.coverExists(bookID):
        coverFilename = db.fullFilePath(f"books/{bookID}/cover{size}.png")
        if os.path.exists(coverFilename):
            return flask.send_file(coverFilename)
    # If book doesnt exist or if book doesnt have cover
    return flask.send_file(f"static/images/bookCoverPlaceholder{size}.png"), 404


@booklist.route("/api/get/<bookID>")
def apiGet(bookID):
    """Respond with the full data of a book"""
    book = db.bookGet(bookID)
    if book:
        return flask.jsonify(book)
    else:
        return {}, 404


@booklist.route("/api/new" , methods=["POST"])
def apiNew():
    """Create a new book and send back the books data"""
    # Invalid request data
    if flask.request.json == None or flask.request.json == {}:
        return {"Success": False}, 422
    # Add to database
    bookID = db.bookAdd(flask.request.json)
    # Book not added
    if not bookID:
        return {"Success": False}, 422
    # Book added, respond with new books ID
    else:
        return {"Success": True, "bookID": bookID}


@booklist.route("/api/edit/<bookID>", methods=["PUT"])
def apiUpdate(bookID):
    """Update a books metadata"""
    if flask.request.json == None or flask.request.json == {}:
        return flask.abort(422)
    # Only edit book if it exists
    if db.bookGet(bookID):
        db.bookEdit(bookID, flask.request.json)
        return {"Success": True}
    else:
        return {"Success": False}, 404


@booklist.route("/api/delete/<bookID>", methods=["DELETE"])
def apiDelete(bookID):
    """Delete a book"""
    # If the book does not exists, return 404
    if not db.bookGet(bookID):
        return {"Deleted": False}, 404
    db.bookDelete(bookID)
    return {"Deleted": True}


@booklist.route("/api/search")
def apiSearch():
    """Search for books based on a query
    
    URL Parameters:
    q = string, search query, default ""
    offset = int, books to skip, default 0
    limit = int, amount of books to return, default 25, max 100"""
    searchStartTime = time.time()
    # Get parameters
    query = flask.request.args.get("q")
    if query == None or query == "":
        bookIDs = list(db.data.keys())[::-1]
    else:
        bookIDs = db.bookSearch(query)
    offset = flask.request.args.get("offset", default=0, type=int)
    limit = flask.request.args.get("limit", default=25, type=int)
    if offset < 0:
        offset = 0
    if limit < 0 or offset > 100:
        limit = 25

    # Get book metadata
    pageOfBookIDs = bookIDs[offset:offset+limit]
    books = []
    for bookID in pageOfBookIDs:
        books.append({"bookID": bookID, **db.bookGet(bookID, search=True)})
    
    # Return books and information about query
    response = {
        "time": int(((time.time() - searchStartTime) * 1000) + 1),
        "first": offset + 1,
        "last":  offset + len(books),
        "total": len(bookIDs),
        "books": books
    }
    return response


if __name__ == "__main__":
    if "--help" in sys.argv:
        print("Joe Baker's APP Assignment BookList")
        print("Usage: ./server.py [options]")
        print("Options:")
        print("  --help            Display this help and exit")
        print("  --host HOST       Set the servers host IP")
        print("  --port PORT       Set the servers port")
        print("  --werkzeug        Use werkzeug instead of waitress")
        print("  --data-dir DIR    Set the directory where data is stored")
        exit()

    # Get host and port from argv or use the defaults
    host = "0.0.0.0"
    port = 80
    if "--host" in sys.argv:
        host = sys.argv[sys.argv.index("--host") + 1]
    if "--port" in sys.argv:
        port = sys.argv[sys.argv.index("--port") + 1]

    # Use waitress as the WSGI server if it is installed,
    # but use built-in if it isnt, or if --werkzeug argument.
    useWaitress = False
    if not "--werkzeug" in sys.argv:
        try:
            import waitress
            useWaitress = True
        except:
            print("Waitress is not installed, using built-in WSGI server (werkzeug).")

    # Startup
    db = database()
    db.load()

    # Run server
    if useWaitress:
        waitress.serve(booklist, host=host, port=port, threads=8)
    else:
        booklist.run(host=host, port=port)

    # Shut down
    print("Saving database...")
    db.save()
