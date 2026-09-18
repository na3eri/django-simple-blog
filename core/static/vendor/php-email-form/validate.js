(function () {
  "use strict";

  /**
   * Password visibility toggle
   */
  window.togglePassword = function (inputId, button) {
    const input = document.getElementById(inputId);

    if (!input) {
      return;
    }

    const icon = button.querySelector("i");

    if (input.type === "password") {
      input.type = "text";

      if (icon) {
        icon.classList.remove("bi-eye");
        icon.classList.add("bi-eye-slash");
      }
    } else {
      input.type = "password";

      if (icon) {
        icon.classList.remove("bi-eye-slash");
        icon.classList.add("bi-eye");
      }
    }
  };


  /**
   * Django form submit helper
   *
   * This function is intentionally simple.
   * Django handles the POST, validation, redirect,
   * authentication and messages.
   */
  function handleDjangoForm(form) {
    form.addEventListener("submit", function () {
      const submitButton = form.querySelector(
        'button[type="submit"], input[type="submit"]'
      );

      if (submitButton) {
        submitButton.disabled = true;
      }

      const loading = form.querySelector(".loading");

      if (loading) {
        loading.classList.add("d-block");
      }
    });
  }


  /**
   * Initialize Django forms
   *
   * Any form with the class "django-form"
   * will use normal browser submission.
   */
  const forms = document.querySelectorAll(".django-form");

  forms.forEach(function (form) {
    handleDjangoForm(form);
  });

})();