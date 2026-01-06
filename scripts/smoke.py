import argparse
import json
import time


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", required=True)
    args = parser.parse_args()

    log = {"started_at": time.time(), "steps": []}

    try:
        # Placeholder for future steps
        pass
    finally:
        with open(args.log, "w", encoding="utf-8") as f:
            json.dump(log, f, indent=2)


if __name__ == "__main__":
    main()
