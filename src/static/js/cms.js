(function () {
  "use strict";

  /*
   * ============================================
   * CMS - Add Button Limits
   * ============================================
   */

  function updateAddButtonStates() {
    // Sliders
    var sliderList = document.getElementById("slider-list");
    var addSliderBtn = document.getElementById("add-slider-btn");

    if (sliderList && addSliderBtn) {
      var sliderCount = sliderList.querySelectorAll(".card").length;

      if (sliderCount >= 4) {
        addSliderBtn.disabled = true;
        addSliderBtn.classList.add("disabled");
      } else {
        addSliderBtn.disabled = false;
        addSliderBtn.classList.remove("disabled");
      }
    }

    // Categories
    var categoryList = document.getElementById("category-list");
    var addCategoryBtn = document.getElementById("add-category-btn");

    if (categoryList && addCategoryBtn) {
      var categoryCount = categoryList.querySelectorAll(".card").length;

      if (categoryCount >= 3) {
        addCategoryBtn.disabled = true;
        addCategoryBtn.classList.add("disabled");
      } else {
        addCategoryBtn.disabled = false;
        addCategoryBtn.classList.remove("disabled");
      }
    }

    // About Images
    var imageList = document.getElementById("about-image-list");
    var addImageBtn = document.getElementById("add-image-btn");

    if (imageList && addImageBtn) {
      var imageCount = imageList.querySelectorAll(".card").length;

      if (imageCount >= 3) {
        addImageBtn.disabled = true;
        addImageBtn.classList.add("disabled");
      } else {
        addImageBtn.disabled = false;
        addImageBtn.classList.remove("disabled");
      }
    }
  }


  /*
   * ============================================
   * CMS - Modal Form Actions
   *
   * Sets the form action dynamically from
   * the clicked button's data-action attribute.
   * ============================================
   */

  function initModalActions() {
    var modals = document.querySelectorAll(".modal");

    modals.forEach(function (modal) {

      modal.addEventListener("show.bs.modal", function (event) {

        var button = event.relatedTarget;

        if (!button) {
          return;
        }

        var action = button.getAttribute("data-action");

        if (!action) {
          return;
        }

        var form = modal.querySelector("form");

        if (!form) {
          return;
        }

        form.setAttribute("action", action);

        console.log("CMS Modal Action Set");
        console.log("Action:", action);
        console.log("Form:", form);
      });
    });
  }


  /*
   * ============================================
   * CMS - Delete Confirmations
   * ============================================
   */

  function initDeleteConfirmations() {
    var deleteButtons = document.querySelectorAll(
      ".btn-delete-slider, .btn-delete-category, .btn-delete-image"
    );

    deleteButtons.forEach(function (btn) {

      btn.addEventListener("click", function (event) {

        var confirmed = window.confirm(
          "Are you sure you want to delete this item?"
        );

        if (!confirmed) {
          event.preventDefault();
        }
      });
    });
  }


  /*
   * ============================================
   * CMS - Image Preview
   * ============================================
   */

  function initImagePreviews() {
    var modals = document.querySelectorAll(".modal");

    modals.forEach(function (modal) {

      var fileInput = modal.querySelector(
        'input[type="file"]'
      );

      var previewContainer = modal.querySelector(
        ".cms-image-preview"
      );

      if (!fileInput) {
        return;
      }

      fileInput.addEventListener("change", function () {

        if (!this.files || !this.files[0]) {
          return;
        }

        var reader = new FileReader();

        reader.onload = function (event) {

          if (!previewContainer) {
            return;
          }

          previewContainer.innerHTML = "";

          var img = document.createElement("img");

          img.src = event.target.result;
          img.className = "img-fluid rounded mt-2";

          img.style.maxHeight = "200px";
          img.style.objectFit = "cover";
          img.style.width = "100%";

          previewContainer.appendChild(img);
        };

        reader.readAsDataURL(this.files[0]);
      });
    });
  }


  /*
   * ============================================
   * CMS - Debug
   * ============================================
   */

  function initDebug() {
    console.log("CMS.JS LOADED");
  }


  /*
   * ============================================
   * CMS - Initialize
   * ============================================
   */

  document.addEventListener("DOMContentLoaded", function () {

    console.log("CMS DOM READY");

    updateAddButtonStates();
    initModalActions();
    initDeleteConfirmations();
    initImagePreviews();
    initDebug();
  });

})();