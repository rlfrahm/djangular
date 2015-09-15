angular.module('App', ['Api', 'ui.bootstrap', 'ui.router'])

.config(['$interpolateProvider', '$stateProvider', '$urlRouterProvider', function($interpolateProvider, $stateProvider, $urlRouterProvider) {
  $interpolateProvider.startSymbol('{[{').endSymbol('}]}');

  // For any unmatched url
  $urlRouterProvider.otherwise('/');

  // States
  $stateProvider
    .state('home', {
      url: '/',
      templateUrl: 'static/partials/home.html'
    })
    .state('profile', {
      url: '/profile',
      templateUrl: 'static/partials/user/profile.html'
    })
    .state('tabs', {
      url: '/tabs/open',
      templateUrl: 'static/partials/drinks/open-tab.html'
    });
}])

.run(['$rootScope', 'Me', function($rootScope, Me) {
  if (!$rootScope.user) {
    $rootScope.user = Me.get(function() {
      console.log($rootScope.user);
    });
  }
}])

.directive('buyDrinks', [function() {
  return {
    scope: true,
    link: function(scope) {
      scope.order = {
        bar: '',
        bartender: '',
        emails: [],
        drinks: [
          { name: 'Beer', cost: 5 }
        ]
      };
      scope.state = 0;
      scope.setState = function(s) {
        scope.state = s;
      };
      scope.isState = function(s) {
        return (s == scope.state);
      };
      scope.addAnotherEmail = function() {
        console.log(scope.order.emails.length - 1, scope.order.emails, scope.order.emails[scope.order.emails.length - 1]);
        if (scope.order.emails[scope.order.emails.length - 1] != '')
          scope.order.emails.push('');
      };
      scope.setType = function(t) {
        scope.order.type = t;
        if (t == 'me')
          scope.order.emails = [email];
        else
          scope.order.emails = [''];
        scope.setState(1);
      };
    }
  };
}]);