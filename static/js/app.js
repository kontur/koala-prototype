/*!  - v0.0.0 - 2014-12-23
* https://github.com/kontur/koala-prototype
* Copyright (c) 2014 ; Licensed  */
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
angular.module('Koala.directives', []).directive('ngEnter', function () {
    return function (scope, element, attrs) {
        element.bind("keydown keypress", function (event) {
            console.log(event);
            if (event.which === 13) {
                scope.$apply(function () {
                    scope.$eval(attrs.ngEnter);
                });

                event.preventDefault();
            }
        });
    };
});

angular.module('Koala', [
    'ngRoute',
    'Koala.controllers',
    'Koala.services',
    'Koala.directives'
    ])
    .config(['$routeProvider', function ($routeProvider) {
        $routeProvider.when('/home', { templateUrl: 'static/partials/home.html', controller: 'HomeController' });

        $routeProvider.when('/here', { templateUrl: 'static/partials/locations.html', controller: 'HereController' });
        $routeProvider.when('/here/explore/:category', { templateUrl: 'static/partials/category.html', controller: 'HereCategoryController' });
        $routeProvider.when('/search/:term', { templateUrl: 'static/partials/locations.html', controller: 'SearchController' });
        $routeProvider.when('/search/:term/explore/:category', { templateUrl: 'static/partials/category.html', controller: 'SearchCategoryController' });

        $routeProvider.when('/location/:id', { templateUrl: 'static/partials/location.html', controller: 'LocationController' });
        $routeProvider.otherwise({ redirectTo: '/home' });
    }]);

angular.module('Koala.services', ['ngResource'])

    .factory('Venue', ['$resource', function ($resource) {
        return $resource('/api/venue/:id', {}, {
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