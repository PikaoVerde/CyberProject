let map, infoWindow;


function initMap(obj) {
console.log("obj from initmap")
console.log(obj)
const israel = { lat: 31.4117257, lng: 35.0818155 }
  const map = new google.maps.Map(document.getElementById("map"), {
    center: israel,
    zoom: 8,
  });

  const infoWindow = new google.maps.InfoWindow();

function addMarker([la, ln, title]) {
  const marker = new google.maps.Marker({
    position : { lat: parseFloat(la), lng: parseFloat(ln)},
    map : map,
    title: `${title}`,
    label: "!",
    optimized: false,
  });
      marker.addListener("click", () => {
      infoWindow.close();
      infoWindow.setContent(marker.getTitle());
      infoWindow.open(marker.getMap(), marker);
    });
}

//google.maps.event.addListener(map, "click", (event) => {
//    addMarker([event.latLng, "click"], map);
//  });

for (let i=0; i<obj.markers.length ;i++)
{
    console.log(obj.markers[i])
    addMarker(obj.markers[i])
}



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

fetch('mapdata').then(function(response){
    return response.json();
}).then(function (obj){
    console.log(obj);
    window.initMap = initMap(obj);
}).catch(function(error){
    console.error('Deu Merda');
    console.error(error);
});
