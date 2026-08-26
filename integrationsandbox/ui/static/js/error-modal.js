document.addEventListener("htmx:responseError", function (evt) {
  var modal = document.getElementById("error-modal");
  var messageEl = document.getElementById("error-modal-message");
  if (!modal || !messageEl) return;

  var message = "Something went wrong.";
  var xhr = evt.detail && evt.detail.xhr;
  if (xhr && xhr.responseText) {
    try {
      var body = JSON.parse(xhr.responseText);
      if (body && body.detail) {
        message = body.detail;
      }
    } catch (e) {
      // Response wasn't JSON; fall back to the default message.
    }
  }

  messageEl.textContent = message;
  modal.showModal();
});
