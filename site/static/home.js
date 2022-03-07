function homePageSetup() {
    const locationList = document.getElementById("locationList");
    const buttons = locationList.getElementsByTagName("button");
    for(const button of buttons) {
      button.addEventListener("click", () => {
        fetch(`/request/${button.id}`, {
          method: "POST",
        }).then( () => {
            window.location.assign(`/request/${button.id}`);
        });
      });
    }
}


function makeLetMeInRequest() {
    
}
