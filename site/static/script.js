function request_ack() {
    element = document.getElementById("notification_header");
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
                        element.innerHTML = "Timed out.";
                    } else if (text === "acked") {
                        element.innerHTML = "Request answered; Sit tight.";
                    }
                });
            } else if (resp.status == 408){
                element.innerHTML = "Timed out.";
            }
        })
}
