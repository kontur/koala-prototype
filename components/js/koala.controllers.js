
angular.module('Koala.controllers', ['geolocation'])
    .controller('HomeController', ['$scope', '$location', function ($scope, $location) {
        console.log("hello home controller");
        $scope.go = function (path) {
            $location.path(path + "/" + $scope.term);
        };
    }])

    .controller('HereController', ['$scope', '$route', 'geolocation', 'Venues', function ($scope, $route, geolocation, Venues) {
        console.log("HereController");
        geolocation.getLocation().then(function(data){
            $scope.coords = {lat: data.coords.latitude, lng: data.coords.longitude};
            $scope.locations = Venues.show({ v1: data.coords.latitude, v2: data.coords.longitude });
        });
    }])

    .controller('SearchController', ['$scope', '$route', 'Venues', function ($scope, $route, Venues) {
        console.log("SearchController");
        $scope.locations = Venues.search({ v1: $route.current.params.term });
    }])

    .controller('LocationController', ['$scope', '$route', 'Venue', function ($scope, $route, Venue) {
        console.log("LocationController", $route.current.params.id );
        $scope.media = Venue.images({ id: $route.current.params.id });
    }])

;