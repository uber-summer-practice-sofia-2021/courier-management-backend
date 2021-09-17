window.onload = function () {
  var script = document.getElementById("script_id");
  var status = script.getAttribute("status");
  var btn_picked = document.getElementById("btn_picked");
  var btn_delivered = document.getElementById("btn_delivered");

  if (status == "PICKED_UP" || status == "COMPLETED") {
    btn_picked.disabled = true;
    btn_delivered.disabled=false;
    document.getElementById('progressbar_picked').className="active";
  }
  if (status == "COMPLETED") {
    btn_delivered.disabled = true;
    document.getElementById('progressbar_delivered').className="active";
  }
};
