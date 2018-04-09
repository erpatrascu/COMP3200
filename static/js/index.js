
function initMap() { }

$(document).ready(function () {

    //initiating the google map, centred on Los Angeles
    var map;
    initMap = function() {
      map = new google.maps.Map(document.getElementById("map"), {
               center: {lat:34.0484733,lng:-118.1387121},
               zoom: 10,
               gestureHandling: 'greedy'
       });
    } 
    
    //adding the google map to the app
    var js_file = document.createElement('script');
    js_file.type = "text/javascript";
    js_file.src = "https://maps.googleapis.com/maps/api/js?key=AIzaSyA8GwI6YMKgOnYwkUs48GWpBDhdyv049Bs&callback=initMap";
    document.getElementsByTagName('head')[0].appendChild(js_file);

  //setting up the date picker and the app outlook  
  $( "#datepicker" ).datepicker({ dateFormat: 'dd-mm-yy' }).datepicker("setDate", new Date());

  $('#wrapper').toggleClass('toggled');

  //used
  var polygons = [];

  //deleting all the drawn polygons when redrawing
  function clearPolygons() {
    while(polygons.length) { 
      polygons.pop().setMap(null); 
    }
    polygons.length = 0;
   }
   
   //adding an info box when clicking on a polygon to show the zipcode number
   infoWindow = null;
   function attachPolygonInformation(polygon, info) {
    infoWindow = new google.maps.InfoWindow();
    google.maps.event.addListener(polygon, 'click', function (e) {
        infoWindow.setContent(info);
        infoWindow.setPosition(e.latLng);
        infoWindow.open(map);
    });
  }

  // getting the predictions results
  $(".setbutton").click(function () {
    var date = $('#datepicker').datepicker().val();
    var shiftTime = $("#shift-select").val();
    var crimeType = $("#crime-select").val();
    //console.log(date + "\n" + shift + "\n" + crime);

    var path = '/getprediction/' + date + '/' + shiftTime + '/' + crimeType;

    // Get results and make them visible in the overlay
    // colours in red for predicted crime and white for no crime predicted
    $.get(path, function (data, status) {
        var zipcodes = JSON.parse(data);
        clearPolygons();
        for (var i = 0; i<zipcodes.length; i++){ 
          if(zipcodes[i]["0"] == 1){
            polygons.push(new google.maps.Polygon({
              paths: JSON.parse((zipcodes[i].geometry).replace(new RegExp("'", 'g'), "\"")),
              strokeColor: '#FF0000',
              strokeOpacity: 0.8,
              strokeWeight: 2,
              fillColor: '#FF0000',
              fillOpacity: 0.35
              }));
            polygon = polygons[polygons.length - 1];
            polygon.setMap(map);
            attachPolygonInformation(polygon, zipcodes[i]["zipcode"].toString()); 
          } else {
            polygons.push(new google.maps.Polygon({
              paths: JSON.parse((zipcodes[i].geometry).replace(new RegExp("'", 'g'), "\"")),
              strokeColor: '#FF0000',
              strokeOpacity: 0.8,
              strokeWeight: 2,
              fillColor: '#FFFFFF',
              fillOpacity: 0.55
              }));
            polygon = polygons[polygons.length - 1];
            polygon.setMap(map);
            attachPolygonInformation(polygon, zipcodes[i]["zipcode"].toString()); 
          }
          
          
        }
    }).fail(function (err) {
      alert("A problem occurred! Make sure you have up to date data for predictions!");
    });
  });

});

