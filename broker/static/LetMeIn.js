var buttID;
var levelAID;
var levelNID;
var levelSID;
var onloadCallback = function () {
    buttID = grecaptcha.render('butt', {
        'sitekey': '6LeFOrkUAAAAAK4ewdAH9kBpsjFgvviwY6nNUWI3',
        'callback': letIn1
    });
    levelAID = grecaptcha.render('levelA', {
        'sitekey': '6LeFOrkUAAAAAK4ewdAH9kBpsjFgvviwY6nNUWI3',
        'callback': letInA
    });
    levelNID = grecaptcha.render('levelN', {
        'sitekey': '6LeFOrkUAAAAAK4ewdAH9kBpsjFgvviwY6nNUWI3',
        'callback': letInN
    });
    levelSID = grecaptcha.render('levelS', {
        'sitekey': '6LeFOrkUAAAAAK4ewdAH9kBpsjFgvviwY6nNUWI3',
        'callback': letInS
    });
}

function validate(event) {
    event.preventDefault();
    grecaptcha.execute();
}

function showElem(id) {
    document.getElementById(id).style.display = "initial";
}

function hideElem(id) {
    document.getElementById(id).style.display = "none";
}

function hideButtons() {
    hideElem("buttonContainer");
}

function processName(inputName) {
    var name = null;
    var processedName = null;
    var numberCheck = /[0-9]/g;
    var gmaCheck = /gma/g;
    try {
        name = inputName;
        processedName = name.trim().toLowerCase().replace(/\s/g, '');
    } catch (e) {
        //console.warning(e);
    }
    if (numberCheck.test(processedName) || gmaCheck.test(processedName) || processedName == "test") {
        name = "false";
        return name;
    } else {
        return name;
    }
}

function letInA(token) {
    letInGeneric('aLevel');
}

function letIn1(token) {
    letInGeneric('1Level');
}

function letInN(token) {
    letInGeneric('nLevel');
}

function letInS(token) {
    letInGeneric('sLevel');
}

function letInGeneric(level) {
    var name = null;
    var checkedName = null;
    try {
        name = prompt('Enter name to alert Slack OR press OK to skip');
        checkedName = processName(name);
    } catch (e) {
        console.warning(e);
    }
    if (checkedName === "") {
        letIn(level);
    } else if (checkedName == null) {
        alert('Your request has been canceled');
    } else if (checkedName === "false") {
        hideButtons();
        showElem("ligmaStatus");
    } else if (checkedName != "" && checkedName != null) {
        postSlack(name, level);
    }
}

function letIn(level) {
    showElem("waitingStatus");
    hideButtons();
    var response;
    var responseButt = grecaptcha.getResponse(buttID);
    var responseLevelA = grecaptcha.getResponse(levelAID);
    var responseLevelN = grecaptcha.getResponse(levelNID);
    var responseLevelS = grecaptcha.getResponse(levelSID);
    if (responseButt == "" && responseLevelN == "" && responseLevelS == "") {
        response = responseLevelA;
    }
    else if (responseButt == "" && responseLevelA == "" && responseLevelS == "") {
        response = responseLevelN;
    }
    else if (responseButt == "" && responseLevelA == "" && responseLevelN == "") {
        response = responseLevelS;
    }
    else {
        response = responseButt;
    }

    var params = {
        level: level,
        response: response
    };

    var json = JSON.stringify(params);

    fetch(`/activate`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: json
    })
        .then(resp => {
            if (resp.ok) {
                hideElem("waitingStatus");
                return resp.text().then(text => {
                    if (text === "timeout") {
                        showElem("timedOutStatus");
                    } else if (text === "buttonpressed") {
                        showElem("comingStatus");
                    }
                });
            }
        })
}

function postSlack(name, level) {
    if (level === "aLevel") {
        levelString = "Level A";
    } else if (level === "1Level") {
        levelString = "Level 1"
    } else if (level === "nLevel") {
        levelString = "North Side Stariwell"
    } else if (level === "sLevel") {
        levelString = "South Side Stairwell"
    }
    var params = {
        "text": `<!subteam^SCL50LELQ> ${name} wants to get in from ${levelString}`
    }
    fetch('/notify', {
        headers: { 'Content-Type': 'application/json' },
        method: 'POST',
        body: JSON.stringify(params)
    })
        .then(() => letIn(level))
        .catch((error) => console.log(error));
}
