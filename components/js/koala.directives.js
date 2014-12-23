angular.module('Koala.directives', [])
    .directive('ngEnter', function () {
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
    })

    .directive('loading', function () {
        return {
            restrict: 'E',
            replace: true,
            template: '<div class="loading"><img src="/static/img/ajax-loader.gif" />loading</div>',
            link: function (scope, element, attr) {
                scope.$watch('loading', function (val) {
                    if (val) {
//                        angular.element(element).show();
                    } else {
                        angular.element(element).remove();
                    }
                });
            }
        };
    })

;