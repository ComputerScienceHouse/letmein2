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
                    request_ack();
                });
            }
        });
      });
    }
}

function request_ack() {
    const notification_header = document.getElementById("request_modal_title");
    const home_link = document.getElementById("request_modal_home_button");
    const cancel_link = document.getElementById("request_modal_cancel_button");
    resetRequestModal();

    fetch(`/anybody_home`, {
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
                        notification_header.innerHTML = "Request answered; Sit tight.";
                        home_link.hidden = false;
                        cancel_link.hidden = true;
                    }
                });
            } else if (resp.status == 408){
                notification_header.innerHTML = "Timed out.";
                // document.getElementById("request_modal_header").style.backgroundColor = "red";
                // notification_header.style.color = "white";
                //document.getElementById("alert_timeout").style.display = "inline"; // TODO: Make this look good.
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
    const home_link = document.getElementById("request_modal_home_button");
    const cancel_link = document.getElementById("request_modal_cancel_button");
    home_link.hidden = true;
    cancel_link.hidden = false;
}