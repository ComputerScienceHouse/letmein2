function request_ack() {
    notification_header = document.getElementById("notification_header");
    home_link = document.getElementById("home_link");
    cancel_link = document.getElementById("cancel_link");
    fetch(`/anybody_home`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
    })
        .then(resp => {
            console.log(resp);
            if (resp.status == 200) { // TODO: Using 408 on the backend broke this
                return resp.text().then(text => {
                    if (text === "timeout") {
                        notification_header.innerHTML = "Timed out.";
                    } else if (text === "acked") {
                        notification_header.innerHTML = "Request answered; Sit tight.";
                        home_link.hidden = false;
                        cancel_link.hidden = true;
                    }
                });
            } else if (resp.status == 408){
                notification_header.innerHTML = "Timed out.";
                home_link.hidden = false;
                cancel_link.hidden = true;
            }
        })
}
