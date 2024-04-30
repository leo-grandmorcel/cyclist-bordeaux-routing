function getitineraire_coo(marqeurs) {
  var depart = [marqeurs[0].getLatLng().lat, marqeurs[0].getLatLng().lng];
  var destination = [marqeurs[1].getLatLng().lat, marqeurs[1].getLatLng().lng];
  $.ajax({
    type: "POST",
    contentType: "application/json; charset=utf-8",
    url: "http://127.0.0.1:8000/iti_coordinate/",
    data: JSON.stringify({ depart: depart, destination: destination }),
    success: function (data) {
      $("#map_base").html(data.map);
    },
  });
}
