import json
import sys
from copy import copy
from datetime import datetime
from pathlib import Path
from subprocess import run

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


def main(kiddo: str) -> None:
    kiddo = kiddo.lower()
    if kiddo not in ("eleanor", "audrey", "leland"):
        raise RuntimeError("Kiddo must be one of 'Eleanor', 'Audrey', or 'Leland'")
    folder_path = HERE / "photos" / kiddo
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
    if len(sys.argv) != 2:
        raise RuntimeError("Must supply one name")
    main(sys.argv[1])
