function forceDownload(blob, filename) {
  var a = document.createElement('a');
  a.download = filename;
  a.href = blob;
  // For Firefox https://stackoverflow.com/a/32226068
  document.body.appendChild(a);
  a.click();
  a.remove();
}

function downloadJson(content, fileName, contentType) {
    var a = document.createElement("a");
    var file = new Blob([content], {type: contentType});
    a.href = URL.createObjectURL(file);
    a.download = fileName;
    a.click();
}

// Current blob size limit is around 500MB for browsers
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

const callback = (mutationList, observer) => {
    var startCallback = Date.now();
    for (const mutation of mutationList) {
        for (const node of mutation.addedNodes) {
            if (node.className.includes("frontend")) {
                more = node.firstChild;
            } else if (node.children.length > 0) {
                for (const n of node.children) {
                    if (n.className.includes("dayLabel")) {
                        date = n.childNodes[0].nodeValue;
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
            }
        }
    }
    var endCallback = Date.now();
    while ((endCallback - startCallback) < 5000) {
        endCallback = Date.now();
    }
    if (more.isVisible()) {
        more.click();
    }
};

const config = { childList: true, subtree: false };
const observer = new MutationObserver(callback);
const targetNode = document.querySelector("div.StudentFeed");
observer.observe(targetNode, config);
var more = targetNode.querySelector("div[class^='frontend']").firstChild;

function go() {
    for (const node of targetNode.children) {
        for (const n of node.children) {
            if (n.className.includes("dayLabel")) {
                if (n.childNodes[0].nodeValue.includes("Today")) {
                    date = `${today.getMonth()}/${today.getDay()}/${today.getFullYear()}`;
                } else if (n.childNodes[0].nodeValue.includes("Yesterday")) {
                    date = `${yesterday.getMonth()}/${yesterday.getDay()}/${yesterday.getFullYear()}`;
                } else {
                    date = n.childNodes[0].nodeValue;
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
    }
    // This triggers the mutation observer
    more.click();
}

function itemToObj(identifier, caption, date, time) {
    let obj = new Object();
    obj.identifier = identifier;
    obj.datetime = new Date(`${date} ${time}`);
    obj.caption = caption;
    dates.push(obj);
}

function finish() {
    let jsonData = JSON.stringify(dates);
    downloadJson(jsonData, "data.json", "application/json");
}
