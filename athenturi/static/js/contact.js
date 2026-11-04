// contact გვერდი: "შეკითხვა" / "ტურის შეძენა" გადამრთველი
(function () {
  "use strict";
  var kind = document.getElementById("kind");
  var fields = document.getElementById("purchaseFields");
  var tour = document.getElementById("tourSelect");
  var tickets = document.getElementById("tickets");
  var label = document.getElementById("messageLabel");
  var message = document.getElementById("message");
  var submit = document.getElementById("submitBtn");
  var totalBox = document.getElementById("totalBox");
  var totalVal = document.getElementById("totalVal");

  function update() {
    var purchase = kind.value === "purchase";
    fields.hidden = !purchase;
    tour.required = purchase;
    tickets.required = purchase;
    message.required = !purchase;
    label.textContent = purchase ? "დამატებითი კომენტარი (არასავალდებულო)" : "თქვენი შეკითხვა";
    submit.textContent = purchase ? "შეძენის მოთხოვნის გაგზავნა" : "გაგზავნა";
    updateTotal();
  }

  function updateTotal() {
    var opt = tour.options[tour.selectedIndex];
    var n = parseInt(tickets.value, 10);
    if (kind.value !== "purchase" || !opt || !opt.value || !n) { totalBox.hidden = true; return; }
    var left = parseInt(opt.dataset.left, 10);
    tickets.max = Math.min(left, 10);
    if (n > left) { tickets.value = left; n = left; }
    totalVal.textContent = "€" + (n * parseInt(opt.dataset.price, 10));
    totalBox.hidden = false;
  }

  kind.addEventListener("change", update);
  tour.addEventListener("change", updateTotal);
  tickets.addEventListener("input", updateTotal);
  update();
})();
