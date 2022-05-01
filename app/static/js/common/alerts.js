function createAlert(msg, alertType, _class) {
  /* Create an alert */

  let alert = document.createElement("div");
  if (_class) {
    alert.className = "alert " + alertType + " " + _class;
  } else {
    alert.className = "alert " + alertType;
  };
  alert.innerHTML = msg;

  return alert;
}

function clearAlerts(_class) {
  /* Clear all alerts active on DOM */
  for (let alert of document.getElementsByClassName(_class)) {
    alert.remove();
  };
};

export { createAlert, clearAlerts };
