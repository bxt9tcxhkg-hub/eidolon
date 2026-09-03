from __future__ import annotations
import argparse
import sys
import uvicorn
from eidolon.core.config import HTTP_PORT


def main() -> int:
    parser = argparse.ArgumentParser(prog="eidolon", description="Eidolon Agent Runtime")
    sub = parser.add_subparsers(dest="command")

    serve = sub.add_parser("serve", help="Startet den Runtime-Server")
    serve.add_argument("--host", default="0.0.0.0")
    serve.add_argument("--port", type=int, default=HTTP_PORT)

    sub.add_parser("chat", help="Startet den Terminal-Chat")
    sub.add_parser("device", help="Device-Verwaltung")
    sub.add_parser("version", help="Version anzeigen")

    args = parser.parse_args()

    if args.command == "serve":
        uvicorn.run("agent_server:app", host=args.host, port=args.port, reload=False)
        return 0
    elif args.command == "version":
        print("Eidolon 0.1.0")
        return 0
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
