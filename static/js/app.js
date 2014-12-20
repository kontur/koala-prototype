/*!  - v0.0.0 - 2014-12-20
* https://github.com/kontur/koala-prototype
* Copyright (c) 2014 ; Licensed  */

angular.module('Koala.controllers', []);

angular.module('Koala', [
    'ngRoute',
    'Koala.controllers',
    'Koala.services'
    ])
    .config(['$routeProvider', function ($routeProvider) {
        $routeProvider.when('/home', { templateUrl: 'static/partials/home.html' });
        $routeProvider.otherwise({ redirectTo: '/home' });
    }]);

angular.module('Koala.services', ['ngResource'])
    .factory('Places', ['$resource', function ($resource) {
        return {
            all: 'something'
        };
    }]);