function homePageSetup() {
    const locationList = document.getElementById("locationList");
    const buttons = locationList.getElementsByTagName("button");
    const requestModal = document.getElementById("request_modal");
    resetRequestModal();
    
    for(const button of buttons) {
      button.addEventListener("click", () => {
        fetch(`/request/${button.id}`, {
            method: "POST",
            headers: {
                'Content-Type': 'application/json'
            },
        }).then( resp => {
            console.log(resp);
            if (resp.status == 200) {
                return resp.text().then(text => {
                    console.log("Requesting access at location: " + text);
                    //window.location.assign(`/request/${button.id}`);
                    requestModal.style.display = "inline";
                    const requestLocation = document.getElementById("request_modal_title");
                    requestLocation.innerText = "Requesting access at: " + text;
                    knock(`${button.id}`);
                });
            }
        });
      });
    }
}

function knock(location) {
    const notification_header = document.getElementById("request_modal_title");
    const home_link = document.getElementById("request_modal_home_button");
    const cancel_link = document.getElementById("request_modal_cancel_button");
    resetRequestModal();
    
    // Set the date we're counting down to
    //var countDownDate = new Date("May 25, 2022 15:37:25").getTime();
    var timeout = 10; // TODO: Get this from the backend.
    var countDownDate = new Date();
    countDownDate.setSeconds(countDownDate.getSeconds() + timeout);
    document.getElementById("timeout_counter").innerHTML = "Pending...";
    document.getElementById("timeout_bar").setAttribute("style", "width: 0%");

    // Update the count down every 1 second
    var timeoutInterval = setInterval(function() {
        // Get today's date and time
        var now = new Date().getTime();
        // Find the distance between now and the count down date
        var distance = countDownDate - now;
        timeoutCounter = document.getElementById("timeout_counter");
        timeoutCounter.innerHTML = Math.floor(distance / 1000) + " s";
        var progress = Math.floor(((distance/1000 - 1)/timeout) * 100);
        if (progress < 0) {
            progress = 0;
        }
        document.getElementById("timeout_bar").setAttribute("style", "width: " + String(progress) + "%");
        if (distance < 0) {
            clearInterval(timeoutInterval);
            timeoutCounter.innerHTML = "EXPIRED";
        }
    }, 1000);

    fetch(`/anybody_home/` + location, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
    })
        .then(resp => {
            console.log(resp);
            if (resp.status == 200) {
                return resp.text().then(text => {
                    if (text === "acked") {
                        // notification_header.innerHTML = "Request answered; Sit tight.";
                        document.getElementById("request_answer_alert").hidden = false;
                        document.getElementById("timeout_div").hidden = true;

                        // document.getElementById("request_modal_header").style.backgroundColor = "#00FF00";
                        home_link.hidden = false;
                        cancel_link.hidden = true;
                        clearInterval(timeoutInterval);
                    }
                });
            } else if (resp.status == 408) {
                // notification_header.innerHTML = "Timed out.";
                document.getElementById("request_timeout_alert").hidden = false;
                document.getElementById("timeout_div").hidden = true;
                // document.getElementById("request_modal_header").style.backgroundColor = "#FF0000";
                home_link.hidden = false;
                cancel_link.hidden = true;
            }
        })
}

function nevermind() {
    fetch(`/nvm`, {
        method: 'GET',
    }).then( () => {
        const requestModal = document.getElementById("request_modal");
        requestModal.style.display = "none";
    });
}

function closeRequestModal() {
    const requestModal = document.getElementById("request_modal");
    requestModal.style.display = "none";
}

function resetRequestModal() {
    // Stuff that should be hidden
    document.getElementById("request_modal_home_button").hidden = true;
    document.getElementById("request_timeout_alert").hidden = true;
    document.getElementById("request_answer_alert").hidden = true;

    // Stuff that should be visible
    document.getElementById("request_modal_cancel_button").hidden = false;
    document.getElementById("timeout_div").hidden = false;
}