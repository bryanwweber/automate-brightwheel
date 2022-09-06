from pathlib import Path
import json
from datetime import datetime
from subprocess import run
from copy import copy

lat = " ".join(map(str, (41.0, 50.0, 47.6052)))
lat_ref = "N"
long = " ".join(map(str, (71.0, 22.0, 58.6596)))
long_ref = "W"

ARGS = [
    "exiftool/exiftool",
    "-overwrite_original",
    f'-GPSLatitude="{lat}"',
    f'-GPSLongitude="{long}"',
    f'-GPSLatitudeRef="{lat_ref}"',
    f'-GPSLongitudeRef="{long_ref}"',
]

HERE = Path(__file__).parent


def pdm_entry():
    import sys
    if len(sys.argv) != 2:
        raise RuntimeError("Must supply one name")
    main(sys.argv[1])


def main(girl: str) -> None:
    girl = girl.lower()
    if girl not in ("eleanor", "audrey"):
        raise RuntimeError("Specify one of 'Eleanor' or 'Audrey'")
    folder_path = HERE / "photos" / girl
    data = json.loads((folder_path / "data.json").read_text())
    data = {d["identifier"]: d for d in data}
    for jpeg in folder_path.glob("*.jpg"):
        print(jpeg.name)
        metadata = data[jpeg.name]
        dt = datetime.fromisoformat(metadata["datetime"].rstrip("Z"))
        dtstr = dt.strftime("%Y:%m:%d %H:%M:%S")
        date = dt.strftime("%Y:%m:%d")
        time = dt.strftime("%H:%M:%S")
        # Copy to avoid carrying arguments between calls to exiftool
        args = copy(ARGS)
        args.extend(
            (
                f'-AllDates="{dtstr}"',
                "-OffsetTime=-04:00",
                "-OffsetTimeOriginal=-04:00",
                "-OffsetTimeDigitized=-04:00",
                f'-GPSDateStamp="{date}"',
                f'-GPSTimeStamp="{time}"',
            )
        )
        if desc := metadata["caption"]:
            args.extend(
                [
                    f'-iptc:Caption-Abstract="{desc}"',
                    f'-XMP-dc:Description="{desc}"',
                    f'-XMP-tiff:ImageDescription="{desc}"',
                    f'-Ducky:Comment="{desc}"',
                ]
            )
        args.append(str(jpeg.resolve()))
        run(args, capture_output=True)


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        raise RuntimeError("Must supply one name")
    main(sys.argv[1])
