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
    if "--help" in sys.argv:
        print("Joe Baker's APP Assignment BookList")
        print("Usage: ./server.py [options]")
        print("Options:")
        print("  --help            Display this help and exit")
        print("  --host HOST       Set the servers host IP")
        print("  --port PORT       Set the servers port")
        print("  --built-in-wsgi   Use flasks built-in WSGI server instead of waitress")
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
        
    if useWaitress:
        waitress.serve(booklist, host=host, port=port)
    else:
        booklist.run(host=host, port=port)
