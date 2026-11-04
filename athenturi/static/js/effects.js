// ათენტური - ეფექტები: გამოჩენა სქროლზე, მრიცხველები, პარალაქსი, კარუსელი
(function () {
  "use strict";
  var still = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Reveal on scroll
  var items = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window && !still) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } });
    }, { threshold: 0.15, rootMargin: "0px 0px -6% 0px" });
    items.forEach(function (el) { io.observe(el); });
  } else {
    items.forEach(function (el) { el.classList.add("in"); });
  }

  // Count-up numbers
  function count(el) {
    var target = parseInt(el.dataset.count, 10), start = null;
    if (still) { el.textContent = target; return; }
    function step(t) {
      if (start === null) start = t;
      var p = Math.min((t - start) / 1400, 1);
      el.textContent = Math.round(target * (1 - Math.pow(1 - p, 3)));
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }
  var nums = document.querySelectorAll("[data-count]");
  if ("IntersectionObserver" in window) {
    var co = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { count(e.target); co.unobserve(e.target); } });
    }, { threshold: 0.6 });
    nums.forEach(function (el) { co.observe(el); });
  } else { nums.forEach(count); }

  // Parallax
  var px = [].slice.call(document.querySelectorAll("[data-parallax]")), ticking = false;
  function parallax() {
    var vh = window.innerHeight;
    px.forEach(function (el) {
      var box = el.parentElement.getBoundingClientRect();
      if (box.bottom < 0 || box.top > vh) return;
      var shift = -(box.top + box.height / 2 - vh / 2) * 0.12;
      el.style.transform = "translate3d(0," + shift.toFixed(1) + "px,0)";
    });
    ticking = false;
  }
  if (px.length && !still) {
    window.addEventListener("scroll", function () { if (!ticking) { ticking = true; requestAnimationFrame(parallax); } }, { passive: true });
    window.addEventListener("resize", parallax);
    parallax();
  }

  // Carousel (scroll-snap with arrow buttons)
  document.querySelectorAll("[data-carousel]").forEach(function (box) {
    var track = box.querySelector(".carousel-track");
    function by(dir) { track.scrollBy({ left: dir * Math.min(track.clientWidth * 0.8, 760), behavior: "smooth" }); }
    var prev = box.querySelector("[data-carousel-prev]"), next = box.querySelector("[data-carousel-next]");
    if (prev) prev.addEventListener("click", function () { by(-1); });
    if (next) next.addEventListener("click", function () { by(1); });
  });
})();
