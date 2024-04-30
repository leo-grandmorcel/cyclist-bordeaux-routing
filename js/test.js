document
  .getElementById("formItineraire")
  .addEventListener("submit", function (event) {
    event.preventDefault();
    var formData = new FormData(this);
    $.ajax({
      type: "POST",
      contentType: "application/json; charset=utf-8",
      url: "http://127.0.0.1:8000/iti_address/",
      data: JSON.stringify({
        depart: formData.get("depart"),
        destination: formData.get("destination"),
      }),
      success: function (data) {
        $("#map_base").html(data.map);
      },
    });
  });
