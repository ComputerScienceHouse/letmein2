let timeoutInterval;

const locationList = document.getElementById("locationList");
const requestModal = document.getElementById("request_modal");
const nameInput = document.getElementById("knock_name_input");
const homeLink = document.getElementById("request_modal_home_button");
const cancelLink = document.getElementById("request_modal_cancel_button");
const timeoutCounter = document.getElementById("timeout_counter");
const timeoutBar = document.getElementById("timeout_bar");
const requestTimeoutAlert = document.getElementById("request_timeout_alert");
const requestNamelessAlert = document.getElementById("request_nameless_alert");
const requestAnswerAlert = document.getElementById("request_answer_alert");
const requestNvmAlert = document.getElementById("request_nvm_alert");
const timeoutDiv = document.getElementById("timeout_div");
const requestTitle = document.getElementById("request_modal_title");
const namelessTitle = document.getElementById("nameless_title");
const tooltipText = document.getElementById("tooltip-text");

// TODO: This feels janky.
// Sets up the event listeners for the various doors specified by the
// template in the webserver
function homePageSetup() {
  resetRequestModal();
  const buttons = locationList.getElementsByTagName("button");
  const input_item = document.getElementById('knock_name_input');
  for (const button of buttons) {
    button.addEventListener("click", () => {
      localStorage.name = input_item.value;
      knockSocket(`${button.id}`);
    });
  }
  input_item.value = localStorage.name ?? "";
}

function knockSocket(location) {
  if (nameInput.value === "") {
    displayNameless();
    return;
  }
  // If we're http, then we'll use an unencrypted websocket (for development)
  let socketProtocol = 'wss';
  if (window.location.protocol === 'http:') {
    socketProtocol = 'ws';
  }
  let host = window.location.host;
  let url = `${socketProtocol}://${host}/knock/socket/${location}`;
  console.log(url);
  const ws = new WebSocket(url);

  ws.onopen = function(){
    console.log("Connected to websocket :)")
    let namePayload = JSON.stringify({"Event": "NAME", "Name": nameInput.value, "Location": location});
    ws.send(namePayload);
    resetRequestModal();
    // openRequestModal();
    cancelLink.addEventListener("click", () => {
      socketNevermind(ws, location);
    });
  }

  ws.onmessage = function(msg) {
    let data = JSON.parse(msg.data);
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
  let nvmPayload = JSON.stringify({"Event": "NEVERMIND", "Location": location});
  console.log(nvmPayload);
  ws.send(nvmPayload);
  requestNvmAlert.hidden = false;
  timeoutDiv.hidden = true;
  homeLink.hidden = false;
  cancelLink.hidden = true;
}

function displayAcknowledge() {
  requestAnswerAlert.hidden = false;
  requestNamelessAlert.hidden = true;
  timeoutDiv.hidden = true;
  homeLink.hidden = false;
  cancelLink.hidden = true;
}

function displayTimeout() {
  timeoutCounter.hidden = true;
  timeoutBar.hidden = true;
  requestTimeoutAlert.hidden = false;
  requestNamelessAlert.hidden = true;
  timeoutDiv.hidden = true;
  homeLink.hidden = false;
  cancelLink.hidden = true;
}

function displayNameless() {
  requestTitle.hidden = true;
  namelessTitle.hidden = false;
  timeoutCounter.hidden = true;
  timeoutBar.hidden = true;
  requestTimeoutAlert.hidden = true;
  requestAnswerAlert.hidden = true;
  requestNvmAlert.hidden = true;
  requestNamelessAlert.hidden = false;
  timeoutDiv.hidden = true;
  homeLink.hidden = false;
  cancelLink.hidden = true;
}

// function openRequestModal() {
//   requestModal.style.display = "inline";
// }

// function closeRequestModal() {
//   requestModal.style.display = "none";
// }

function resetRequestModal() {
  // Stuff that should be hidden
  homeLink.hidden = true;
  requestTimeoutAlert.hidden = true;
  requestNamelessAlert.hidden = true;
  requestAnswerAlert.hidden = true;
  requestNvmAlert.hidden = true;
  namelessTitle.hidden = true;

  // Stuff that should not be hidden
  cancelLink.hidden = false;
  timeoutDiv.hidden = false;
  requestTitle.hidden = false;
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

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

function toggleLocationButtons() {
  const now = new Date();
  var expirationDate = undefined;
  if (nameInput.value === '') {
    if(locationList.classList.contains('enable-buttons-container')) {
      locationList.classList.remove('enable-buttons-container');
    }
    locationList.classList.add('disable-buttons-container');
    tooltipText.textContent="Enter your name to begin!";
    expirationDate = new Date(now.getTime() - 1 * 60 * 60 * 1000); // expired an hour ago; invalidates cookie
  }
  else {
    if(locationList.classList.contains('disable-buttons-container')) {
      locationList.classList.remove('disable-buttons-container');
    }
    locationList.classList.add('enable-buttons-container');
    tooltipText.textContent="Where are you?";
    expirationDate = new Date(now.getTime() + 2190 * 60 * 60 * 1000); // expires 3 months from submission
  }
  const expires = "expires=" + expirationDate.toUTCString();
  document.cookie = `username=${nameInput.value}; expires=${expires}; path=/`;
}
nameInput.addEventListener('input',toggleLocationButtons);

const username = getCookie("username")
if (getCookie("username") != undefined) { 
  console.log("Cookie found: " + getCookie("username"));
  nameInput.value = username;
} else {
  nameInput.value = ""; // will not work because modern browsers ignore autocomplete=off but one can hope
}

//toggle the map image
function toggleImage() {
  var imgContainer = document.getElementById('imageContainer');
  imgContainer.style.display = (imgContainer.style.display === 'none' || imgContainer.style.display === '') ? 'block' : 'none';
}
toggleLocationButtons();

homePageSetup();
