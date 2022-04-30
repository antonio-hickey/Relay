import { createAlert, clearAlerts } from "./../common/alerts.js";
import { getCredentials } from "./../common/client.js";
import { base } from "./../common/links.js";


function keysModalToggle() {
  /* Toggles the display of keys modal */
  keysModal = document.getElementById('keysModal');
  keysModal.style.display = keysModal.style.display == "block" ? "none" : "block";
};

document.addEventListener("DOMContentLoaded", () => {
  /* Upon page load */

  /*
    Handle the sign-up proccess upon the
    sumbit button being clicked triggering
    a POST request to the sign-up endpoint
    to then display our keys to store in a 
    modal window.
  */

  var sumbit_btn = document.getElementById("sign-in-sumbit-btn");
  sumbit_btn.setAttribute("data-toggle", "");

  sumbit_btn.onclick = (_) => {
    clearAlerts("sign-up-result");

    let credentials = getCredentials();

    fetch(base + "/user/sign-up", {
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      method: "POST",
      body: JSON.stringify(credentials)
    }).then(resp => resp.json())
      .then(data => {
        let status_div = document.getElementById("status");
        let status;
        if ('error_code' in data) {
          let msg = "<strong>Failed!</strong> " + data['msg'];
          status = createAlert(msg, "alert-danger", "sign-up-result");
        } else {
          let msg = "<strong>Success!</strong>";
          status = createAlert(msg, "alert-success", "sign-up-result");
        };
        status.setAttribute("role", "alert");
        status_div.appendChild(status);

        if ('content' in data) {
          let internalKeyInput = document.getElementById('internal-key-text');
          internalKeyInput.value = data['content']['internal_key'];

          let privateKeyDivTextArea = document.getElementById('private-key-text');
          privateKeyDivTextArea.value = data['content']['private_key'];

          keysModalToggle();
          document.getElementById('has-saved-keys-btn').onclick = () => {
            window.location = base + "/web-app/sign-in"
          };
        };
      });
  };
});

