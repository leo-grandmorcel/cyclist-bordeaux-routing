function getitineraire_coo(marqeurs) {
  document.body.classList.add("loading");
  document.querySelector(".overlay").style.display = "block";
  var depart = [marqeurs[0].getLatLng().lat, marqeurs[0].getLatLng().lng];
  var destination = [marqeurs[1].getLatLng().lat, marqeurs[1].getLatLng().lng];
  $.ajax({
    type: "POST",
    contentType: "application/json; charset=utf-8",
    url: "http://127.0.0.1:8000/iti_coordinate/",
    data: JSON.stringify({ depart: depart, destination: destination }),
    success: function (data) {
      $("#map_base").html(data.map);
      document.body.classList.remove("loading");
      document.querySelector(".overlay").style.display = "none";
    },
  });
}

async function getaddress_coo(latitude, longitude) {
  return fetch(
    `http://127.0.0.1:8000/address?latitude=${latitude}&longitude=${longitude}`
  )
    .then((response) => response.json())
    .then((data) => {
      return data;
    });
}
