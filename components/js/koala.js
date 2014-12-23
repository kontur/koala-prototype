
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