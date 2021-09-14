window.onload = function () {
  var script = document.getElementById("script_id");
  var status = script.getAttribute("status");
  console.log(status);
  var btn_picked = document.getElementById("btn_picked");
  var btn_delivered = document.getElementById("btn_delivered");
  if (status == "picked_up" || status == "completed") {
    btn_picked.disabled = true;
    document.getElementById('progressbar_picked').className="active";
  }
  if (status == "completed") {
    btn_delivered.disabled = true;
    document.getElementById('progressbar_delivered').className="active";
  }
};
