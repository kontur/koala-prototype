
angular.module('Koala.controllers', ['geolocation'])
    .controller('HomeController', ['$scope', '$location', function ($scope, $location) {
        console.log("hello home controller");
        $scope.go = function (path) {
            $location.path(path + "/" + $scope.term);
        };
    }])
    .controller('NearbyController', ['$scope', '$route', 'geolocation', 'Places', function ($scope, $route, geolocation, Places) {
        console.log("hello nearby controller");
        geolocation.getLocation().then(function(data){
            $scope.coords = {lat: data.coords.latitude, lng: data.coords.longitude};
            console.log(data.coords);
            $scope.locations = Places.search({ lat: data.coords.latitude, lng: data.coords.longitude });
            console.log($scope.locations);
        });
    }])
    .controller('SearchController', ['$scope', '$route', 'Places', function ($scope, $route, Places) {
        console.log("hello search controller");
        $scope.term =  $route.current.params.term;
        console.log(Places.get());
    }])
    .controller('LocationController', ['$scope', '$route', 'PlaceMedia', function ($scope, $route, PlaceMedia) {
        console.log("hello location controller", $route.current.params.id );
        $scope.media = PlaceMedia.images({ id: $route.current.params.id });
    }])

;