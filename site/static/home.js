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
    // button.addEventListener("click", () => {
    //   fetch(`/request/${button.id}`, {
    //     method: "POST",
    //     headers: {
    //       "Content-Type": "application/json",
    //     },
    //   }).then(async (resp) => {
    //     if (resp.status == 200) {
    //       const text = await resp.text();
    //       requestModal.style.display = "inline";
    //       const requestLocation = document.getElementById(
    //         "request_modal_title"
    //       );
    //       requestLocation.innerText = "Requesting access at: " + text;
    //       knock(button.id);
    //     }
    //   });
    // });
  }

  const knockButton = document.getElementById("socketCountdown");
  knockButton.addEventListener("click", () => {
    knockSocket("test");
  })
}

async function fetchTimeout() {
  const response = await fetch("/session_info/", {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });
  const timeoutPeriodText = await response.text();
  return parseInt(timeoutPeriodText);
}

/* After the MQTT request returns 200, this function will wait for a 200 from the
backend signaling that someone has answered the request. If it times out, it should
also receive a 403 that signals that the request could not be answered. */
async function knock(location) {
  resetRequestModal();
  const timeout = await fetchTimeout(); // TODO: Get this from the backend.
  const countDownDate = new Date();
  countDownDate.setSeconds(countDownDate.getSeconds() + timeout);
  timeoutCounter.innerHTML = `${timeout} s`;
  timeoutBar.style.width = 0;
  timeoutBar.style.width = "100%";
  timeoutInterval = setInterval(function () {
    let now = new Date().getTime();
    let timeUntilTimeout = countDownDate - now;
    let progress = Math.ceil((timeUntilTimeout / 1000 / timeout) * 100);
    if (progress < 0) progress = 0;
    timeoutCounter.innerHTML = Math.ceil(timeUntilTimeout / 1000) + " s";
    timeoutBar.style.width = `${progress}%`;
    if (timeUntilTimeout < -1000) {
      clearInterval(timeoutInterval);
      timeoutCounter.hidden = true;
      timeoutBar.hidden = true;
    }
  }, 1000);

  fetch(`/anybody_home/${location}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
  }).then(async (knockResp) => {
    if (knockResp.status == 200) {
      const text = await knockResp.text();
      if (text === "acked") {
        requestAnswerAlert.hidden = false;
        timeoutDiv.hidden = true;
        homeLink.hidden = false;
        cancelLink.hidden = true;
        clearInterval(timeoutInterval);
      }
    } else if (knockResp.status == 403) {
      await new Promise((r) => setTimeout(r, 1000)); // Delay to let the animation finish (this is fucking cursed)
      requestTimeoutAlert.hidden = false;
      timeoutDiv.hidden = true;
      homeLink.hidden = false;
      cancelLink.hidden = true;
    }
  });
}

// Cancels a request
function nevermind() {
  fetch("/nvm", {
    method: "POST",
  }).then(() => {
    requestNvmAlert.hidden = false;
    timeoutDiv.hidden = true;
    homeLink.hidden = false;
    cancelLink.hidden = true;
    clearInterval(timeoutInterval);
  });
}

function socketNevermind(ws) {
  ws.send("NEVERMIND");
  requestNvmAlert.hidden = false;
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

function knockSocket(location) {
  url = 'ws://localhost:8080/knock/socket/' + location;
  ws = new WebSocket(url);

  ws.onopen = function(){
    console.log("Connected to websocket :)")
    resetRequestModal();
    openRequestModal();
    cancelLink.addEventListener("click", () => {
      socketNevermind(ws);
    });
  }

  ws.onmessage = function(msg) {
    data = JSON.parse(msg.data);
    console.log(data)
    if (data.Event === "COUNTDOWN") {
      // Apply a 1 second offset to make animation look good.
      updateTimeoutBar(data.CurrentTime - 1, data.MaxTime - 1);
    } else if (data.Event === "ACKNOWLEDGE") {
      requestAnswerAlert.hidden = false;
      timeoutDiv.hidden = true;
      homeLink.hidden = false;
      cancelLink.hidden = true;
    } else if (data.Event === "TIMEOUT") {
      timeoutCounter.hidden = true;
      timeoutBar.hidden = true;

      requestTimeoutAlert.hidden = false;
      timeoutDiv.hidden = true;
      homeLink.hidden = false;
      cancelLink.hidden = true;
    }
  }
}

homePageSetup();
