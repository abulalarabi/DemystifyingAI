"""Serve DemystifyingAI and its API from one process."""

import argparse


def port_number(raw):
    port = int(raw)
    if not 1 <= port <= 65535:
        raise argparse.ArgumentTypeError("port must be between 1 and 65535")
    return port


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1", help="address to bind (default: %(default)s)")
    parser.add_argument("--port", type=port_number, default=1407, help="port to bind (default: %(default)s)")
    args = parser.parse_args()

    try:
        from waitress import serve
        from backend.backend import app
    except ModuleNotFoundError as error:
        parser.exit(1, f"Missing Python dependency ({error.name}). Install with: python -m pip install -r requirements.txt\n")

    host = f"[{args.host}]" if ":" in args.host else args.host
    print(f"Starting DemystifyingAI at http://{host}:{args.port}", flush=True)
    serve(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
