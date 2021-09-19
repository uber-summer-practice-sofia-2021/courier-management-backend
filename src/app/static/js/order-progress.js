window.onload = function () {
  var script = document.getElementById("script_id");
  var status = script.getAttribute("status");
  var btn_picked = document.getElementById("btn_picked");
  var btn_delivered = document.getElementById("btn_delivered");
  var pb_picked = document.getElementById('progressbar_picked');
  var pb_delivered = document.getElementById('progressbar_delivered');

  if (status == "PICKED_UP" || status == "COMPLETED") {
    btn_picked.disabled = true;
    btn_delivered.disabled = false;
    pb_picked.className = "active";
  }
  if (status == "COMPLETED") {
    btn_delivered.disabled = true;
    pb_delivered.className = "active";
  }
  if (status == "CANCELLED") {
    pb_picked.className = "cancelled";
    pb_delivered.className = "cancelled";
  }
};