
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