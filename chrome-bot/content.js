console.log("OpenAssistant activating...");

// if (document.URL.indexOf(' blacklisted URLs here ') == -1)

function removeElementsByTag(rootelem, blocktype) {
  let scripts = rootelem.getElementsByTagName(blocktype);
  for (let s of scripts) {
    s.remove();
  }
}
// Split allText into N-sized chunks but keep the last word of each chunk intact
function splitText(text, N) {
  if (typeof text !== "string") {
    throw new Error("Input must be a string");
  }
  if (typeof N !== "number" || N <= 0) {
    throw new Error("Chunk size must be a positive integer");
  }

  let chunks = [];
  let words = text.split(" ");
  let chunk = "";

  for (let i = 0; i < words.length; i++) {
    if (chunk.length + words[i].length < N) {
      chunk += words[i] + " ";
    } else {
      chunks.push(chunk);
      chunk = words[i] + " ";
    }
  }
  chunks.push(chunk);
  return chunks;
}

appendOAStyles = () => {
  var style = document.createElement("style");

  style.innerHTML =
    "\
  .modal {\
    display: none;\
    position: fixed;\
    z-index: 1;\
    left: 0;\
    top: 0;\
    width: 300px;\
    height: 100%;\
    overflow: auto; \
    background-color: rgb(0, 0, 0); \
    background-color: rgba(0, 0, 0, 0.4);\
  }\
  \
  .modal-content {\
    background-color: #fefefe;\
    margin: 15% auto;\
    padding: 20px;\
    border: 1px solid #888;\
    width: 80%;\
  }\
  \
  .close-button {\
    color: #aaa;\
    float: right;\
    font-size: 28px;\
    font-weight: bold;\
  }\
  \
  .close-button:hover,\
  .close-button:focus {\
    color: black;\
    text-decoration: none;\
    cursor: pointer;\
  }\
";
};

// Replace ASK_ENDPOINT with your own endpoint
// We call if with JSON payload {"prompt": "Question"}
// And expect a JSON response {"summ": "Answer"}

ASK_ENDPOINT = "https://MYENDPOINT.COM/ask";

async function remoteAsk(blocks, question) {
  let reply = await fetch(ASK_ENDPOINT, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      prompt: blocks[0] + question,
    }),
  });
  try {
    const data = await reply.json();
    console.log(data["summ"]);
    const oa = document.getElementById("oa-output");
    oa.innerHTML = data["summ"];
    oa.style.backgroundColor = "#ccc";
  } catch (error) {
    console.error(`Error: ${error}`);
    const oa = document.getElementById("oa-output");
    oa.innerHTML = "ERROR";
  }
}

function retrieveText() {
  let allText = "";

  const allEls = [document.body];
  for (const el of allEls) {
    clonedBody = el.cloneNode(true);

    divElements = clonedBody.querySelectorAll("div");
    for (c of divElements) {
      const newNode = document.createElement("span");
      newNode.textContent = " ";
      c.insertBefore(newNode, c.firstChild);
    }

    removeElementsByTag(clonedBody, "script");
    removeElementsByTag(clonedBody, "button");
    removeElementsByTag(clonedBody, "input");

    allText += clonedBody.textContent;
    console.log(clonedBody.textContent);
  }
  return allText;
}

function handleAsk() {
  const splitPoint = 5000;
  console.log("ask");
  const allText = retrieveText();
  const oainput = document.getElementById("oa-input");
  const question = oainput.value;
  console.log(question);
  const blocks = splitText(allText, splitPoint);
  console.log(blocks);

  // Replace remote_ask with local_ask if you want to run the bot inside the browser

  try {
    remoteAsk(blocks, question);
  } catch (error) {
    console.error(`Error in remoteAsk: ${error}`);
  }
}

function createUI() {
  appendOAStyles();

  oadiv = document.createElement("div");
  oadiv.innerHTML =
    '<div class="modal">\
  <div class="modal-content">\
  <!-- call foo() when the button is clicked -->\
    Ask OpenAssistant: <input type="text" id="oa-input" name="oa-input" value="Key takeaways of this page?">\
    <button id="oa-input-click">Ask</button>\
    <span class="close-button">&times;</span>\
    <div id="oa-output"></div>\
    \
  </div>\
  </div>\
  ';

  document.body.prepend(oadiv);
  document
    .getElementById("oa-input-click")
    .addEventListener("click", handleAsk, false);

  const modal = document.querySelector(".modal");
  const closeButton = document.querySelector(".close-button");

  // When the user clicks on <span> (x), close the modal
  closeButton.onclick = function () {
    modal.style.display = "none";
  };

  // When the user clicks anywhere outside of the modal, close it
  window.onclick = function (event) {
    if (event.target == modal) {
      modal.style.display = "none";
    }
  };
  return modal;
}

const modal = createUI();
const timeToInit = 2000;

setTimeout(function () {
  modal.style.display = "block";
  console.log("show UI");
}, timeToInit);
