
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