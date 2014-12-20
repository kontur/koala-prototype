
angular.module('Koala.services', ['ngResource'])
    .factory('Places', ['$resource', function ($resource) {
        return {
            all: 'something'
        };
    }]);