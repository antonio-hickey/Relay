import { createAlert, clearAlerts } from "./../common/alerts.js";
import { getCredentials } from "./../common/client.js";
import { base, comsPage } from "./../common/links.js";

document.addEventListener("DOMContentLoaded", () => {
  /* Upon sign in page is loaded */

  /*
    Handle sign in proccess upon user
    clicking the sign in button. We then
    trigger a POST request to the sign in
    endpoint to recieve and store our token.
  */
  let signInBtn = document.getElementById("sign-in-submit-btn");
  signInBtn.onclick = () => {
    clearAlerts("sign-in-results");

    let credentials = getCredentials();

    fetch(base + "/user/sign-in", {
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      },
      method: "POST",
      body: JSON.stringify(credentials)
    }).then(resp => resp.json())
      .then(data => {
        let status_div = document.getElementById("status");
        let status;

        if ('error_code' in data) {
          let msg = "<strong>Failed!</strong> " + data['msg'];
          status = createAlert(msg, "alert-danger", "sign-in-results");
          status.setAttribute("role", "alert");
          status_div.appendChild(status);
        } else {
          let msg = "<strong>Success!</strong>";
          status = createAlert(msg, "alert-success", "sign-in-results");
          status.setAttribute("role", "alert");
          status_div.appendChild(status);

          sessionStorage.setItem("sessionToken", data["session_token"])

          setTimeout(() => { window.location = comsPage; }, 500);
        };
      })
      .catch((error) => { console.log(error) });
  };
});
