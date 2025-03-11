document.addEventListener("DOMContentLoaded", function () {
  "use strict";

  // =================================
  // Back to top button
  // =================================
  $(document).ready(function () {
    // Show or hide the button when scrolling
    $(window).scroll(function () {

      if ($(this).scrollTop() > 200) {
        $("#back-to-top").fadeIn();
        $("#back-to-top").css("bottom", "20px");
      } else {
        $("#back-to-top").fadeOut();
        $("#back-to-top").css("bottom", "-200px");
      }
  
    });
  
    // Smooth scroll to top when button is clicked
    $("#back-to-top").click(function (e) {
      $("html, body").animate({ scrollTop: 0 }, 100);
      return false;
    });

  });
  // =================================

});