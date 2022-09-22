import json
from pathlib import Path
from datetime import datetime
from string import Template
from base64 import standard_b64encode
from subprocess import run

import jmespath


HERE = Path(__file__).parent


def pdm_entry() -> None:
    import sys

    if len(sys.argv) != 2:
        raise RuntimeError("Pass only one argument to the script")
    output = standard_b64encode(main(sys.argv[-1]).encode("utf-8")).decode()
    run(["printf", f'"\\e]52;c;{output}\\e\\\\"'])


def main(girl: str) -> str:
    girl = girl.lower()
    if girl not in ("eleanor", "audrey"):
        raise RuntimeError("Girl must be one of 'Eleanor' or 'Audrey'")

    data = json.loads((HERE / "photos" / girl / "data.json").read_text())
    datetimes = jmespath.search("[*].datetime", data)
    last_dt_seen = sorted(datetime.fromisoformat(dt[:-1]) for dt in datetimes)[-1]
    last_date_seen = last_dt_seen.strftime("%m/%d/%Y")

    output = "\n".join(
        (
            forceDownload,
            downloadJson,
            downloadResource,
            itemToObj,
            getPhoto.substitute(last_date_seen=last_date_seen),
            callback,
            go,
            finish,
            globalVars,
        )
    )

    print(output)
    return output


go = """\
function go() {
    for (const node of targetNode.children) {
        shouldBreak = getPhoto(node);
        if (shouldBreak) {
            more = null;
            break;
        }
    }
    // This triggers the mutation observer
    if (more) {
        more.click();
    }
}
"""

callback = """\
const callback = (mutationList, observer) => {
    var startCallback = Date.now();
    for (const mutation of mutationList) {
        for (const node of mutation.addedNodes) {
            if (node.className.includes("frontend")) {
                more = node.firstChild;
            } else if (node.children.length > 0) {
                shouldBreak = getPhoto(node);
                if (shouldBreak) {
                    more = null;
                    break;
                }
            }
        }
    }
    var endCallback = Date.now();
    while ((endCallback - startCallback) < 5000) {
        endCallback = Date.now();
    }
    if (more && more.checkVisibility()) {
        more.click();
    }
};
"""

forceDownload = """\
function forceDownload(blob, filename) {
    let a = document.createElement('a');
    a.download = filename;
    a.href = blob;
    // For Firefox https://stackoverflow.com/a/32226068
    document.body.appendChild(a);
    a.click();
    a.remove();
}
"""

downloadJson = """\
function downloadJson(content, fileName, contentType) {
    let a = document.createElement("a");
    let file = new Blob([content], {type: contentType});
    a.href = URL.createObjectURL(file);
    a.download = fileName;
    a.click();
}
"""

downloadResource = r"""
function downloadResource(url, filename) {
  if (!filename) filename = url.split('\\').pop().split('/').pop();
  fetch(url, {
      headers: new Headers({
        'Origin': location.origin
      }),
      mode: 'cors'
    })
    .then(response => response.blob())
    .then(blob => {
      let blobUrl = window.URL.createObjectURL(blob);
      forceDownload(blobUrl, filename);
    })
    .catch(e => console.error(e));
}
"""

globalVars = """\
var today = new Date();
var yesterday = new Date(new Date().setDate(new Date().getDate() - 1));
var date;
var time;
var href;
var identifier;
var content;
var captions;
var caption;
var dates = new Array();
const config = { childList: true, subtree: false };
const observer = new MutationObserver(callback);
const targetNode = document.querySelector("div.StudentFeed");
observer.observe(targetNode, config);
var more = targetNode.querySelector("div[class^='frontend']").firstChild;
var shouldBreak = false;
"""

itemToObj = """\
function itemToObj(identifier, caption, date, time) {
    let obj = new Object();
    obj.identifier = identifier;
    obj.datetime = new Date(`${date} ${time}`);
    obj.caption = caption;
    dates.push(obj);
}
"""

finish = """\
function finish() {
    let jsonData = JSON.stringify(dates);
    downloadJson(jsonData, "data.json", "application/json");
}
"""

getPhoto = Template("""\
function getPhoto(node) {
    for (const n of node.children) {
        if (n.className.includes("dayLabel")) {
            date = n.childNodes[0].nodeValue;
            if (date.includes("Today")) {
                date = `$${today.getMonth() + 1}/$${today.getDate()}/$${today.getFullYear()}`;
            } else if (date.includes("Yesterday")) {
                date = `$${yesterday.getMonth() + 1}/$${yesterday.getDate()}/$${yesterday.getFullYear()}`;
            }
            if (date == "$last_date_seen") {
                observer.disconnect();
                return true;
            }
        } else if (n.className.includes("card-module-card")) {
            time = n.querySelector("span[class^='activity-card-module-date']").firstChild.textContent;
            content = n.querySelector("div[class^='activity-card-module-content']");
            href = content.getElementsByTagName('a')[0].href;
            identifier = href.split("?")[0].split("/").at(-1);
            caption = content.querySelector("p[class^='activity-card-module-text']")?.textContent;
            if (caption === undefined) {
                caption = ""
            }
            itemToObj(identifier, caption, date, time);
            downloadResource(href, identifier);
        }
    }
    return false;
}
""")
