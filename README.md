# automate-brightwheel

Automate the [Brightwheel] website to download pictures.

## Step 1

Go to [brightwheel] and log in. Choose one of the kids, then the "Feed" link at the top. Filter the feed to only show photos.

## Step 2

Run

```shell
task source NAME=<name>
```

where `<name>` is either `eleanor` or `audrey`, case insensitive. This will print the generated js source to the terminal and hopefully also copy it to the system clipboard.

## Step 3

Paste the generated js source into the Chrome console in the tab where [Brightwheel] is loaded. Then, start the script with

```console
go()
```

When the pictures are all downloaded, in the console run

```console
finish()
```

to download the `data.json` file.

## Step 4

Move the pictures from the `Downloads` folder to `./photos/<name>`. Move the `data.json` to the root of this source tree.

## Step 5

Merge the existing and new `data.json` files with

```shell
task merge NAME=<name>
```

Then delete the `data.json` file in the root.

## Step 6

Edit the EXIF data of the photos with

```shell
task exif NAME=<name>
```

## Step 7

Upload the modified files to Google Photos and add them to the Brightwheel shared album.

## Initial (new machine) setup

Install [mise]. Then run

```shell
mise install
```

[brightwheel]: https://mybrightwheel.com
[mise]: https://mise.jdx.dev
