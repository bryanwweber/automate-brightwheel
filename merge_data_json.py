import json
import sys
from pathlib import Path

HERE = Path(__file__).parent


def main(kiddo: str) -> None:
    kiddo = kiddo.lower()
    if kiddo not in ("eleanor", "audrey", "leland"):
        raise RuntimeError("Pass one of 'Eleanor', 'Audrey', or 'Leland'")

    existing_data = HERE / "photos" / kiddo / "data.json"
    d1 = json.loads(existing_data.read_text())
    d2 = json.loads((HERE / "data.json").read_text())
    existing_data.write_text(json.dumps(d1 + d2))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise RuntimeError("Pass one argument")
    main(sys.argv[1])
