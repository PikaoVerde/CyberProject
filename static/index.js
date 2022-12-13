//import data from './mapdata.json' assert { type: 'JSON' };
//
//console.log(data);
let map, infoWindow;


function initMap() {
const israel = { lat: 31.4117257, lng: 35.0818155 };
  map = new google.maps.Map(document.getElementById("map"), {
    center: israel,
    zoom: 8,
  });
  infoWindow = new google.maps.InfoWindow();

//  const iconBase ="http://maps.google.com/mapfiles/kml/"
//
//  const icons = {
//  danger:{icon: iconBase + shapes/caution.png}
//  };

  const marker = new google.maps.Marker({
    position: { lat: 32.1778, lng: 34.8736 },
    map: map,
    draggable: true
  });

  const locationButton = document.createElement("button");

  locationButton.textContent = "Pan to Current Location";
  locationButton.classList.add("custom-map-control-button");
  map.controls[google.maps.ControlPosition.TOP_CENTER].push(locationButton);
  locationButton.addEventListener("click", () => {
    // Try HTML5 geolocation.
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const pos = {
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          };

          infoWindow.setPosition(pos);
//          infoWindow.setContent("Location found.");
//          infoWindow.open(map);
          map.setCenter(pos);
          map.setZoom(14)
        },
        () => {
          handleLocationError(true, infoWindow, map.getCenter());
        }
      );
    } else {
      // Browser doesn't support Geolocation
      handleLocationError(false, infoWindow, map.getCenter());
    }

  });
}

function handleLocationError(browserHasGeolocation, infoWindow, pos) {
  infoWindow.setPosition(pos);
  infoWindow.setContent(
    browserHasGeolocation
      ? "Error: The Geolocation service failed."
      : "Error: Your browser doesn't support geolocation."
  );
  infoWindow.open(map);
}

window.initMap = initMap;
