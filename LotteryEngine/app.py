from flask import Flask
from web.routes import routes

import argparse

app = Flask(__name__)
app.register_blueprint(routes)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--runserver", action="store_true")
    args = parser.parse_args()

    if args.runserver:
        print(f"Running server on http://{args.host}:{args.port}")
        app.run(host=args.host, port=args.port, debug=True)
    else:
        parser.print_help()
