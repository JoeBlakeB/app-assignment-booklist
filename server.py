#!/usr/bin/env python3

import flask
import sys


booklist = flask.Flask(__name__)


@booklist.route("/")
def sendIndex():
    return flask.send_file("html/index.html")


@booklist.route("/static/<path:path>")
def sendStatic(path):
    return flask.send_from_directory("static", path)


@booklist.route("/placeholderimage")
def placeholderImage():
    return flask.send_file("/home/joe/Pictures/Memes/Hoodcate/HoodCate.png")
    

if __name__ == "__main__":
    # Use waitress as the WSGI server if it is installed,
    # but use built-in if it isnt, or if --built-in-wsgi argument.
    useWaitress = False
    if not "--built-in-wsgi" in sys.argv:
        try:
            import waitress
            useWaitress = True
        except:
            print("Waitress is not installed, using built-in WSGI server.")
        
    if useWaitress:
        waitress.serve(booklist, host="0.0.0.0", port=80)
    else:
        booklist.run(host="0.0.0.0", port=80)
