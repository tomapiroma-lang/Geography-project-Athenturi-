// ათენტური - საერთო სკრიპტი (ნავიგაცია, flash, პაროლის ჩვენება, header)
(function () {
  "use strict";

  var toggle = document.getElementById("navToggle");
  var menu = document.getElementById("navMenu");
  if (toggle && menu) {
    toggle.addEventListener("click", function () {
      var open = menu.classList.toggle("open");
      toggle.setAttribute("aria-expanded", String(open));
    });
    menu.addEventListener("click", function (e) {
      if (e.target.closest("a")) { menu.classList.remove("open"); toggle.setAttribute("aria-expanded", "false"); }
    });
  }

  document.querySelectorAll(".flash-close").forEach(function (btn) {
    btn.addEventListener("click", function () { btn.parentElement.remove(); });
  });
  document.querySelectorAll(".flash-success, .flash-info").forEach(function (el) {
    setTimeout(function () { el.remove(); }, 7000);
  });

  document.querySelectorAll(".pw-toggle").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var input = btn.parentElement.querySelector("input");
      input.type = input.type === "password" ? "text" : "password";
    });
  });

  var year = document.getElementById("year");
  if (year) year.textContent = new Date().getFullYear();

  var header = document.getElementById("siteHeader");
  function onScroll() { header.classList.toggle("is-scrolled", window.scrollY > 10); }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();
})();
