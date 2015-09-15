angular.module('App', ['Api', 'ui.bootstrap', 'ui.router'])

.config(['$interpolateProvider', '$stateProvider', '$urlRouterProvider', '$locationProvider', '$httpProvider', function($interpolateProvider, $stateProvider, $urlRouterProvider, $locationProvider, $httpProvider) {
  $interpolateProvider.startSymbol('{[{').endSymbol('}]}');

  // Remove hashbang
  $locationProvider.html5Mode(true)

  // Add csrf token security
  $httpProvider.defaults.xsrfCookieName = 'csrftoken';
  $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';

  // For any unmatched url
  $urlRouterProvider.otherwise('/');

  // States
  $stateProvider
    .state('home', {
      url: '/',
      templateUrl: 'static/partials/home.html'
    })
    .state('logout', {
      url: '/logout',
      templateUrl: 'static/partials/user/logout.html',
      controller: function($scope) {
        $scope.logout();
      }
    })
    .state('profile', {
      url: '/profile',
      templateUrl: 'static/partials/user/profile.html'
    })
    .state('tabs', {
      url: '/tabs/open',
      templateUrl: 'static/partials/drinks/open-tab.html'
    })
    .state('bars', {
      url: '/bars',
      templateUrl: 'static/partials/bars/search.html'
    })
    .state('bars-mine', {
      url: '/bars/mine',
      templateUrl: 'static/partials/bars/mine.html',
      controller: 'UserBarsCtrl'
    })
    .state('bar-detail', {
      url: '/bars/:id',
      templateUrl: 'static/partials/bars/bar-detail.html',
      controller: 'BarCtrl'
    })
    .state('bars-add', {
      url: '/bars/mine/add',
      templateUrl: 'static/partials/bars/add.html',
      controller: 'BarAddCtrl'
    })
    .state('bar-settings', {
      url: '/bars/:id/settings',
      templateUrl: 'static/partials/bars/bar-settings.html',
      controller: 'BarSettingsCtrl'
    });
}])

.run(['$rootScope', '$state', 'Auth', 'Me', function($rootScope, $state, Auth, Me) {
  if (!$rootScope.user) {
    $rootScope.user = Me.get(function() {
      console.log($rootScope.user);
    });
  }

  $rootScope.logout = function() {
    var status = Auth.logout(function() {
      document.cookie = "sessionid=; expires=Thu, 01 Jan 1970 00:00:00 UTC";
      // window.location.reload(true);
      $state.go($state.current.name, $state.params, { reload: true });
    });
  };
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
}])

.directive('tabs', [function() {
  return {
    scope: true,
    link: function(scope) {
      scope.state = 0;
      scope.setState = function(s) {
        scope.state = s;
      };
      scope.isState = function(s) {
        return (s == scope.state);
      };
    }
  };
}])

.directive('focus', [function() {
  return {
    link: function(scope, element) {
      element[0].focus();
    }
  };
}]);