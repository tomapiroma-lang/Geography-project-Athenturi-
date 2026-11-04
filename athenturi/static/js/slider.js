// მთავარი გვერდის სლაიდერი: ავტომატური გადასვლა, წერტილები, ისრები, swipe
(function () {
  "use strict";
  var root = document.querySelector("[data-slider]");
  if (!root) return;
  var slides = [].slice.call(root.querySelectorAll(".slide"));
  var dots = [].slice.call(root.querySelectorAll(".dot"));
  var counter = root.querySelector("[data-current]");
  var interval = parseInt(root.dataset.interval, 10) || 7000;
  var still = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var index = 0, timer = null, paused = false;
  root.style.setProperty("--dur", interval + "ms");
  if (still) root.classList.add("no-auto");

  function go(n) {
    index = (n + slides.length) % slides.length;
    slides.forEach(function (s, i) { s.classList.toggle("is-active", i === index); s.setAttribute("aria-hidden", String(i !== index)); });
    dots.forEach(function (d, i) {
      d.classList.remove("is-active");
      if (i === index) { void d.offsetWidth; d.classList.add("is-active"); }   // restart the progress line
    });
    if (counter) counter.textContent = "0" + (index + 1);
    schedule();
  }
  function schedule() {
    clearTimeout(timer);
    if (still || paused) return;
    timer = setTimeout(function () { go(index + 1); }, interval);
  }
  function pause(p) { paused = p; root.classList.toggle("is-paused", p); if (p) clearTimeout(timer); else schedule(); }

  root.querySelector("[data-next]").addEventListener("click", function () { go(index + 1); });
  root.querySelector("[data-prev]").addEventListener("click", function () { go(index - 1); });
  dots.forEach(function (d, i) { d.addEventListener("click", function () { go(i); }); });
  root.addEventListener("mouseenter", function () { pause(true); });
  root.addEventListener("mouseleave", function () { pause(false); });
  root.addEventListener("focusin", function () { pause(true); });
  root.addEventListener("focusout", function () { pause(false); });
  document.addEventListener("visibilitychange", function () { pause(document.hidden); });
  root.addEventListener("keydown", function (e) {
    if (e.key === "ArrowRight") go(index + 1);
    if (e.key === "ArrowLeft") go(index - 1);
  });

  var x0 = null;
  root.addEventListener("touchstart", function (e) { x0 = e.touches[0].clientX; }, { passive: true });
  root.addEventListener("touchend", function (e) {
    if (x0 === null) return;
    var dx = e.changedTouches[0].clientX - x0;
    if (Math.abs(dx) > 50) go(index + (dx < 0 ? 1 : -1));
    x0 = null;
  });

  go(0);
})();
