#!/usr/bin/env python3

import flask
import os
import sys

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
    if db.bookExists(bookID):
        coverFilename = db.fullFilePath(f"books/{bookID}/cover{size}.png")
        if os.path.exists(coverFilename):
            return flask.send_file(coverFilename)
    # If book doesnt exist or if book doesnt have cover
    return flask.send_file(f"static/images/bookCoverPlaceholder{size}.png"), 404


@booklist.route("/api/new", methods=["POST"])
def apiNew():
    pass


@booklist.route("/api/update/<bookID>", methods=["PUT"])
def apiUpdate(bookID):
    pass


@booklist.route("/api/delete/<bookID>")
def apiDelete(bookID):
    pass


@booklist.route("/api/search/<query>")
def apiSearch(bookID):
    pass


if __name__ == "__main__":
    if "--help" in sys.argv:
        print("Joe Baker's APP Assignment BookList")
        print("Usage: ./server.py [options]")
        print("Options:")
        print("  --help            Display this help and exit")
        print("  --host HOST       Set the servers host IP")
        print("  --port PORT       Set the servers port")
        print("  --built-in-wsgi   Use flasks built-in WSGI server instead of waitress")
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
    # but use built-in if it isnt, or if --built-in-wsgi argument.
    useWaitress = False
    if not "--built-in-wsgi" in sys.argv:
        try:
            import waitress
            useWaitress = True
        except:
            print("Waitress is not installed, using built-in WSGI server.")

    # Startup
    db = database()
    db.load()

    # Run server
    if useWaitress:
        waitress.serve(booklist, host=host, port=port)
    else:
        booklist.run(host=host, port=port)

    # Shut down
    print("Saving database...")
    db.save()
