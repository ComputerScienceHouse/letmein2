let timeoutInterval;

const locationList = document.getElementById("locationList");
const requestModal = document.getElementById("request_modal");
const homeLink = document.getElementById("request_modal_home_button");
const cancelLink = document.getElementById("request_modal_cancel_button");
const timeoutCounter = document.getElementById("timeout_counter");
const timeoutBar = document.getElementById("timeout_bar");
const requestTimeoutAlert = document.getElementById("request_timeout_alert");
const requestAnswerAlert = document.getElementById("request_answer_alert");
const requestNvmAlert = document.getElementById("request_nvm_alert");
const timeoutDiv = document.getElementById("timeout_div");
const requestTitle = document.getElementById("request_modal_title");

// TODO: This feels janky.
// Sets up the event listeners for the various doors specified by the
// template in the webserver
function homePageSetup() {
  resetRequestModal();
  const buttons = locationList.getElementsByTagName("button");
  for (const button of buttons) {
    button.addEventListener("click", () => {
      knockSocket(`${button.id}`);
    });
  }
}

function knockSocket(location) {
  url = 'ws://localhost:8080/knock/socket/' + location;
  ws = new WebSocket(url);

  ws.onopen = function(){
    console.log("Connected to websocket :)")
    resetRequestModal();
    openRequestModal();
    cancelLink.addEventListener("click", () => {
      socketNevermind(ws, location);
    });
  }

  ws.onmessage = function(msg) {
    data = JSON.parse(msg.data);
    console.log(data)
    if (data.Event === "LOCATION") {
      requestTitle.innerText = "Requesting Access at " + data.Location
    } else if (data.Event === "COUNTDOWN") {
      // Apply a 1 second offset to make animation look good.
      updateTimeoutBar(data.CurrentTime - 1, data.MaxTime - 1);
    } else if (data.Event === "ACKNOWLEDGE") {
      displayAcknowledge();
    } else if (data.Event === "TIMEOUT") {
      displayTimeout();
    }
  }
}

function socketNevermind(ws, location) {
  let nvmPayload = JSON.stringify({Event: "NEVERMIND", location: location})
  ws.send(nvmPayload);
  requestNvmAlert.hidden = false;
  timeoutDiv.hidden = true;
  homeLink.hidden = false;
  cancelLink.hidden = true;
}

function displayAcknowledge() {
  requestAnswerAlert.hidden = false;
  timeoutDiv.hidden = true;
  homeLink.hidden = false;
  cancelLink.hidden = true;
}

function displayTimeout() {
  timeoutCounter.hidden = true;
  timeoutBar.hidden = true;
  requestTimeoutAlert.hidden = false;
  timeoutDiv.hidden = true;
  homeLink.hidden = false;
  cancelLink.hidden = true;
}

function openRequestModal() {
  requestModal.style.display = "inline";
}

function closeRequestModal() {
  requestModal.style.display = "none";
}

function resetRequestModal() {
  // Stuff that should be hidden
  homeLink.hidden = true;
  requestTimeoutAlert.hidden = true;
  requestAnswerAlert.hidden = true;
  requestNvmAlert.hidden = true;

  // Stuff that should not be hidden
  document.getElementById("request_modal_cancel_button").hidden = false;
  document.getElementById("timeout_div").hidden = false;

  timeoutCounter.hidden = false;
  timeoutBar.hidden = false;

  // Reset width of bar.
  timeoutBar.style.width = 0;
}

function updateTimeoutBar(currentTime, maxTime) {
  let progress = Math.ceil((currentTime / maxTime) * 100);
  if (progress < 0) progress = 0;
  timeoutCounter.innerHTML = currentTime + " s";
  timeoutBar.style.width = `${progress}%`;
  if (currentTime < -1000) {
    // clearInterval(timeoutInterval);
    timeoutCounter.hidden = true;
    timeoutBar.hidden = true;
  }
}

homePageSetup();
