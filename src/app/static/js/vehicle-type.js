$(document).ready(function () {
  function changeMins() {
    weight = $("#package-max-weight")[0];
    width = $("#package-max-width")[0];
    length = $("#package-max-length")[0];
    height = $("#package-max-height")[0];
    buttons = $(".radio-custom:checked")[0];

    switch (buttons.id) {
      case "car-btn":
        weight.min = "10";
        weight.placeholder = weight.min;
        width.min = "1.0";
        width.placeholder = width.min;
        height.min = "0.5";
        height.placeholder = height.min;
        length.min = "1.0";
        length.placeholder = length.min;
        break;

      case "bicycle-btn":
        weight.min = "3";
        weight.placeholder = weight.min;
        width.min = "0.3";
        width.placeholder = width.min;
        height.min = "0.3";
        height.placeholder = height.min;
        length.min = "0.3";
        length.placeholder = length.min;
        break;

      case "van-btn":
        weight.min = "40";
        weight.placeholder = weight.min;
        width.min = "1.5";
        width.placeholder = width.min;
        height.min = "1";
        height.placeholder = height.min;
        length.min = "2";
        length.placeholder = length.min;
        break;
     
    }
  }

  changeMins();
  buttons = $(".radio-custom");
  for(var btn of buttons)
  {
      console.log(btn)
      btn.addEventListener('change', changeMins);
  }
});
