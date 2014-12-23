/*!  - v0.0.0 - 2014-12-23
* https://github.com/kontur/koala-prototype
* Copyright (c) 2014 ; Licensed  */

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

    .controller('LocationController', ['$scope', '$route', 'PlaceMedia', function ($scope, $route, PlaceMedia) {
        console.log("LocationController", $route.current.params.id );
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
        $routeProvider.when('/here', { templateUrl: 'static/partials/locations.html', controller: 'HereController' });
        $routeProvider.when('/search/:term', { templateUrl: 'static/partials/locations.html', controller: 'SearchController' });
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

    .factory('Venues', ['$resource', function ($resource) {
        return $resource('/api/venues/:action/:v1/:v2/:v3', {
            v1: '@v1',
            v2: '@v2',
            v3: '@v3'
        }, {
            'show': {
                params: { action: 'show' },
                method: 'GET',
                isArray: true
            },
            'search': {
                params: { action: 'search' },
                method: 'GET',
                isArray: true
            }
        });
    }])

;