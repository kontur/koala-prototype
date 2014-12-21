/*!  - v0.0.0 - 2014-12-21
* https://github.com/kontur/koala-prototype
* Copyright (c) 2014 ; Licensed  */

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
    .controller('SearchController', ['$scope', '$route', 'PlaceSearch', function ($scope, $route, PlaceSearch) {
        console.log("hello search controller");
        console.log("term", $route.current.params.term);
        console.log(PlaceSearch.search($route.current.params.term));
    }])
    .controller('LocationController', ['$scope', '$route', 'PlaceMedia', function ($scope, $route, PlaceMedia) {
        console.log("hello location controller", $route.current.params.id );
        $scope.media = PlaceMedia.images({ id: $route.current.params.id });
    }])

;

angular.module('Koala', [
    'ngRoute',
    'Koala.controllers',
    'Koala.services'
    ])
    .config(['$routeProvider', function ($routeProvider) {
        $routeProvider.when('/home', { templateUrl: 'static/partials/home.html', controller: 'HomeController' });
        $routeProvider.when('/nearby', { templateUrl: 'static/partials/nearby.html', controller: 'NearbyController' });
        $routeProvider.when('/search/:term', { templateUrl: 'static/partials/search.html', controller: 'SearchController' });
        $routeProvider.when('/location/:id', { templateUrl: 'static/partials/location.html', controller: 'LocationController' });
        $routeProvider.otherwise({ redirectTo: '/home' });
    }]);
angular.module('Koala.services', ['ngResource'])
    .factory('Places', ['$resource', function ($resource) {
        return $resource('/location_search/:lat/:lng', {}, {
            'search': {
                method: 'GET',
                isArray: true
            }
        });
    }])
    .factory('PlaceSearch', ['$resource', function ($resource) {
        return $resource('/location/name/:name', {}, {
            'search': {
                method: 'GET',
                isArray: true
            }
        });
    }])
    .factory('PlaceMedia', ['$resource', function ($resource) {
        return $resource('/location_media/:id', {}, {
            'images': {
                method: 'GET',
                isArray: true
            }
        });
    }])

;