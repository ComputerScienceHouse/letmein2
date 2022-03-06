function request_ack() {
    element = document.getElementById("notification_header");
    fetch(`/response_acked`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
    })
        .then(resp => {
            if (resp.ok) {
                return resp.text().then(text => {
                    if (text === "timeout") {
                        element.innerHTML = "Timed out.";
                    } else if (text === "buttonpressed") {
                        element.innerHTML = "Request answered; Sit tight.";
                    }
                });
            }
        })
}
