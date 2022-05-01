import { base } from "./links.js"

function sessionRequest(endpoint, payload) {
  return fetch(base + endpoint, {
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
    },
    method: "POST",
    body: JSON.stringify(payload)
  })
};


export { sessionRequest };
