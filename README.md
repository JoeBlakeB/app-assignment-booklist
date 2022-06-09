# APP Assignment Booklist

Joe Baker's Application of Programming Principles Assignment.

This recieved 100/100 marks.

## Usage

To start the server run:

`./server.py`

The default host is `0.0.0.0` and port is `80` and you can change it with the `--host` and `--port`:

`./server.py --host 127.0.0.1 --port 8080`

Data is stored in `./data` and this can be changed with `--data-dir`:

`./server.py --data-dir /path/to/data/directory/`

By default waitress will be used as the WSGI if it is installed and will use werkzeug (the built-in WSGI) if it isn't. To force the server to only use werkzeug add the `--werkzeug` argument:

`./server.py --werkzeug`

To stop the server send a KeyboardInterrupt (ctrl + C).

## Dependencies

- Python 3.7+
- Flask
- Waitress (optional; werkzeug will be used if not installed)
- Pillow (optional; used for resizing uploaded book cover images)
- Requests (only required for testing.py)

## Misc

- Copyright © JoeBlakeB (Joe Baker), All Rights Reserved
- Server tested with Python 3.10.4 on Linux and Windows
- Client tested with Firefox and Chrome on Linux, Windows, and Android
- Button icon SVGs from [Papirus Icon Theme](https://github.com/PapirusDevelopmentTeam/papirus-icon-theme)
