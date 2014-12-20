
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