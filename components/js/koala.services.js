angular.module('Koala.services', ['ngResource'])
    .factory('Places', ['$resource', function ($resource) {
        return $resource('/location_search/:lat/:lng', {}, {
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