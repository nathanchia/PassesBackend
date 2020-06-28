"use strict";
(function() {
  window.onload = function() {
    setup();
  };

  function setup() {
    document.querySelector("button").onclick = ()=> {
      let newPass = document.querySelector("input").value;
      if (newPass) {
        let url = window.location;
        let token = new URLSearchParams(url.search).get("t");
        fetch('https://nkchia.pythonanywhere.com/reset', {
          method: 'POST',
          headers: {
              Accept: 'application/json',
              'Content-Type': 'application/json',
              Authorization: 'Bearer ' + token,
          },
          body: JSON.stringify(
            {newPassword : newPass}
          )
        }).then((response) => {
          if (response.status === 200) {
            window.location.href = 'https://nkchia.pythonanywhere.com/success';
          } else if (response.status === 401) {
            window.location.href = 'https://nkchia.pythonanywhere.com/expire';
          }
        }).catch((error) => {
          // To be implemented
        });
      }
    };
  }
})();