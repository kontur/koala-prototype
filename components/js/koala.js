
angular.module('Koala', [
    'ngRoute',
    'Koala.controllers',
    'Koala.services'
    ])
    .config(['$routeProvider', function ($routeProvider) {
        $routeProvider.when('/home', { templateUrl: 'static/partials/home.html' });
        $routeProvider.otherwise({ redirectTo: '/home' });
    }]);