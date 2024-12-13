import json
import sys
from pathlib import Path

HERE = Path(__file__).parent


def main(girl: str) -> None:
    girl = girl.lower()
    if girl not in ("eleanor", "audrey"):
        raise RuntimeError("Pass one of 'Eleanor' or 'Audrey'")

    existing_data = HERE / "photos" / girl / "data.json"
    d1 = json.loads(existing_data.read_text())
    d2 = json.loads((HERE / "data.json").read_text())
    existing_data.write_text(json.dumps(d1 + d2))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise RuntimeError("Pass one argument")
    main(sys.argv[1])
