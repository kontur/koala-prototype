angular.module('Koala.controllers', ['geolocation'])
    .controller('HomeController', ['$scope', '$location',
        function ($scope, $location) {
            console.log("hello home controller");
            $scope.go = function (path) {
                $location.path(path + "/" + $scope.term);
            };
        }])

    .controller('HereController', ['$scope', '$route', 'geolocation', 'Venues',
        function ($scope, $route, geolocation, Venues) {
            console.log("HereController");
            $scope.uriPart = "here";
            geolocation.getLocation().then(function (data) {
                $scope.locations = Venues.show({ v1: data.coords.latitude, v2: data.coords.longitude });
            });
        }])

    .controller('HereCategoryController', ['$scope', '$route', 'geolocation', 'Venues',
        function ($scope, $route, geolocation, Venues) {
            console.log("HereCategoryController");
            geolocation.getLocation().then(function (data) {
                $scope.places = Venues.show({ v1: data.coords.latitude, v2: data.coords.longitude, v3: $route.current.params.category });
            });
        }])

    .controller('SearchController', ['$scope', '$route', 'Venues',
        function ($scope, $route, Venues) {
            console.log("SearchController");
            $scope.uriPart = "search/" + $route.current.params.term;
            $scope.locations = Venues.search({ v1: $route.current.params.term });
        }])

    .controller('SearchCategoryController', ['$scope', '$route', 'Venues',
        function ($scope, $route, Venues) {
            $scope.places = Venues.search({ v1: $route.current.params.term, v2: $route.current.params.category });
        }])

    .controller('LocationController', ['$scope', '$route', 'Venue',
        function ($scope, $route, Venue) {
            console.log("LocationController", $route.current.params.id);
            $scope.media = Venue.images({ id: $route.current.params.id });
        }])

;