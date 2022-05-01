import { sessionRequest } from "./relay.js"
import { signInPage } from "./links.js"


function getCredentials() {
  /* Grab user credentials */
  return {
    "username": document.getElementById("username").value,
    "password": document.getElementById("password").value,
  };
};


function tokenAuth() {
  /* Authenticate client session token */

  if (sessionStorage.getItem("sessionToken") == null) {
    window.location = signInPage;
  } else {
    const token = (sessionStorage.getItem("sessionToken"))
    sessionRequest(
      "/user/token-check",
      { "session_token": token },
    ).then(resp => resp.json())
      .then(data => {
        if (data["status_code"] != 200) {
          window.location = signInPage;
        };
      });
  };
};


export { getCredentials, tokenAuth }
