// tours გვერდი: რეგიონების dropdown
(function () {
  "use strict";
  var items = document.querySelectorAll(".dropdown");

  function setOpen(item, open) {
    var head = item.querySelector(".dropdown-head");
    var panel = item.querySelector(".dropdown-panel");
    item.classList.toggle("open", open);
    head.setAttribute("aria-expanded", String(open));
    panel.hidden = !open;
  }

  items.forEach(function (item) {
    item.querySelector(".dropdown-head").addEventListener("click", function () {
      var willOpen = !item.classList.contains("open");
      setOpen(item, willOpen);
      if (willOpen && history.replaceState) history.replaceState(null, "", "#" + item.id);
    });
  });

  // #athens და მსგავსი ბმულით მისვლისას შესაბამისი dropdown იხსნება
  function openFromHash() {
    var id = location.hash.slice(1);
    var target = id && document.getElementById(id);
    if (target && target.classList.contains("dropdown")) {
      setOpen(target, true);
      target.scrollIntoView({ behavior: "smooth", block: "start" });
      return true;
    }
    return false;
  }
  window.addEventListener("hashchange", openFromHash);
  // ბმულის გარეშე პირველი რეგიონი ღიაა, რომ გვერდი ცარიელი არ ჩანდეს
  if (!openFromHash() && items.length) setOpen(items[0], true);
})();
