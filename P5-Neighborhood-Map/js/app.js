/**
 * GeoLocation API is only allowed in HTTPS mode from Chrome 50 and above.
 * I request that you run the app either using Firefox or Edge or use a local server.
 * Otherwise, the app will use Delhi as the location.
 * NOTE: While the said behaviour has been reported on w3schools and stackoverflow,
 * I tested running the index.html file directly in chrome v58 on Ubuntu 17.04 and it works as expected.
 *
 */

var position;
var map, infoWindow, viewModel;
/**
 * The ViewModel for our KOs. This will contain all the necessary data
 * @constructor
 */
var ViewModel = function (lat, lng) {

    var self = this;
    self.errorDisplay = ko.observable('');
    self.loc = ko.observable('You');
    self.placesList = ko.observableArray([]);

    // Make an AJAX request to HERE maps service for the location data
    $.ajax({
        url: 'https://places.cit.api.here.com/places/v1/discover/explore?app_code=BA_htwfxmxCfktu3QCXt_A'
        + '&app_id=6Wf32oib8gSt41udwTd4&pretty=true',
        headers: {
            'Geolocation': 'geo:' + lat + ',' + lng,
            'X-Mobility-Mode': 'none'
        },
        dataType: 'json',
        success: function (response) {
            // strip the HTML from location if found
            console.log(JSON.stringify(response));
            self.loc(response.search.context.location.address.text.replace(/<\/?[^>]+(>|$)/g, " "));
            var places = response.results.items;
            places.forEach(self.addToList);
            self.setClickListener();
            self.currentMapItem = self.placesList[0];
        },
        error: function () {
            self.errorDisplay('Could not connect to HERE!');
        }

    });

    // Add data to list and add markers on map
    self.addToList = function (item) {
        self.placesList.push(new google.maps.Marker({
            position: {
                lat: item.position[0],
                lng: item.position[1]
            },
            map: map,
            name: item.title,
            area: item.vicinity,
            rating: item.averageRating,
            show: ko.observable(true),
            selected: ko.observable(false),
            animation: google.maps.Animation.DROP
        }));
    };

    self.doBounce = function (place) {
        place.setAnimation(google.maps.Animation.BOUNCE);
        setTimeout(function () {
            place.setAnimation(null);
        }, 1000);
    };

    // Set a click listener for each marker
    self.setClickListener = function () {
        for (var i = 0; i < self.placesList().length; i++) {
            (function (thisPlace) {
                thisPlace.addListener('click', function () {
                    console.log('clicked ' + thisPlace);
                    self.setSelected(thisPlace);
                });
            })(self.placesList()[i]);
        }
    };

    self.setAllDeselected = function () {
        for (var i = 0; i < self.placesList().length; i++){
            self.placesList()[i].selected(false);
        }
    };

    self.setSelected = function (place) {

        self.setAllDeselected();
        place.selected(true);
        console.log('SELECTED!');

        self.currentMapItem = place;

        var windowContent = '<div>';
        windowContent += '<h4>'+ place.name + '</h4>';
        windowContent += '<p>'+ place.area +'</p>';
        windowContent += '<p> Average User Rating: '+ place.rating +'</p>';
        windowContent += '</div>';

        infoWindow.setContent(windowContent);

        infoWindow.open(map, place);
        self.doBounce(place);
    };

    self.filterText = ko.observable('');

    self.setAllVisible = function (doShow) {
        for (var i = 0; i < self.placesList().length; i++){
            self.placesList()[i].show(doShow);
            self.placesList()[i].setVisible(true);
        }
    };
    self.applyFilter = function () {
        var currentFilter = self.filterText().toLowerCase();

        infoWindow.close();
        if (currentFilter.length === 0) {
            self.setAllVisible(true);
        } else {
            for (var i = 0; i < self.placesList().length; i++){
                if (self.placesList()[i].name.toLowerCase().indexOf(currentFilter) > -1) {
                    self.placesList()[i].show(true);
                    self.placesList()[i].setVisible(true);
                } else {
                    self.placesList()[i].show(false);
                    self.placesList()[i].setVisible(false);
                }
            }
        }
    }

};


function initMap() {
    navigator.geolocation.getCurrentPosition(function (pos) {
        position = pos;
        initAll(pos.coords.latitude, pos.coords.longitude)
    }, function () {
        window.alert('Could not get location! Using Delhi for display');
        initAll(28.6139, 77.2090);
    })
}

function initAll(lat, lng) {

    $(".preloader-div").fadeOut("slow");

    map = new google.maps.Map(
        document.getElementById('map'),
        {
            center: {lat: lat, lng: lng},
            zoom: 13,
            mapTypeControl: false
        }
    );
    infoWindow = new google.maps.InfoWindow();
    viewModel = new ViewModel(lat, lng);
    ko.applyBindings(viewModel);
}

function error() {
    $(".preloader-div").fadeOut("slow");
    $('#errorSpan').text("Failed to initialize Google Maps :( ");
}