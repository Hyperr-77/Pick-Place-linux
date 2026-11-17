import argparse

def start(args) -> None:
    print("Starting client...")

def stop(args: argparse._ArgumentGroup) -> None:
    print("Stopping client...")

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    start_parser = subparsers.add_parser(
        "start",
        help="Start the Pick&Place client"
    )
    start_parser.set_defaults(handler=start)

    stop_parser = subparsers.add_parser(
        "stop",
        help="Stop the Pick&Place client"
    )
    stop_parser.set_defaults(handler=stop)

    args = parser.parse_args()
    args.handler(args)
    return 0