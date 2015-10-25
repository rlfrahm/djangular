angular.module('App', ['Init', 'Api', 'ui.bootstrap', 'ui.router', 'toastr'])

.config(['$interpolateProvider', '$stateProvider', '$urlRouterProvider', '$locationProvider', '$httpProvider', function($interpolateProvider, $stateProvider, $urlRouterProvider, $locationProvider, $httpProvider) {
  $interpolateProvider.startSymbol('{[{').endSymbol('}]}');

  // Remove hashbang
  $locationProvider.html5Mode(true);

  // Add csrf token security
  $httpProvider.defaults.xsrfCookieName = 'csrftoken';
  $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';

  // For any unmatched url
  $urlRouterProvider.otherwise('/');

  // States
  $stateProvider
    // .state('home', {
    //   url: '/',
    //   templateUrl: 'static/partials/home.html',
    //   controller: 'HomeCtrl'
    // })
    .state('logout', {
      url: '/logout',
      templateUrl: 'static/partials/user/logout.html',
      controller: function($scope) {
        $scope.logout();
      }
    })
    .state('profile', {
      url: '/profile',
      templateUrl: 'static/partials/user/profile.html',
      controller: 'UserProfileCtrl'
    })
    .state('tab', {
      url: '/',
      templateUrl: 'static/partials/drinks/tab.html',
      controller: 'TabCtrl'
    })
    .state('tabs-open', {
      url: '/tabs/open',
      templateUrl: 'static/partials/drinks/open-tab.html',
      controller: 'TabOpenCtrl'
    })
    .state('tabs-open.for', {
      url: '/for',
      templateUrl: 'static/partials/drinks/open-tab.for.html',
      controller: function($scope) {
        $scope.order.title = 'Open a tab for';
      }
    })
    .state('tabs-open.find', {
      url: '/find',
      templateUrl: 'static/partials/drinks/open-tab.find.html',
      controller: function($scope) {
        $scope.order.title = 'For who?';
      }
    })
    .state('tabs-open.amount', {
      url: '/amount',
      templateUrl: 'static/partials/drinks/open-tab.amount.html',
      controller: function($scope, $state) {
        $scope.order.title = 'How much?';
      }
    })
    .state('tabs-open.summary', {
      url: '/confirm',
      templateUrl: 'static/partials/drinks/open-tab.summary.html',
      controller: function($scope, $state) {
        $scope.order.title = 'Confirm order';
      }
    })
    .state('bars', {
      url: '/bars',
      templateUrl: 'static/partials/bars/search.html',
      controller: 'BarsCtrl'
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
      controller: 'BarAddCtrl',
      access: {
        permissions: ['BarOwner'],
        permissionType: 'or'
      }
    })
    .state('bar-settings', {
      url: '/bars/:id/settings',
      templateUrl: 'static/partials/bars/bar-settings.html',
      controller: 'BarSettingsCtrl'
    })
    .state('bar-settings.general', {
      url: '/general',
      templateUrl: 'static/partials/bars/bar-settings-general.html'
    })
    .state('bar-settings.financial', {
      url: '/financial',
      templateUrl: 'static/partials/bars/bar-settings-financial.html'
    })
    .state('bar-settings.bartenders', {
      url: '/bartenders',
      templateUrl: 'static/partials/bars/bar-settings-bartenders.html'
    })
    .state('bar-settings.sales', {
      url: '/sales',
      templateUrl: 'static/partials/bars/bar-settings-sales.html'
    })
    .state('user', {
      url: '/user/:id',
      templateUrl: 'static/partials/user/user.html',
      controller: 'UserHandler'
    });
}])

.run(['$rootScope', '$state', 'Auth', 'Me', 'Authorization', '$sce', 'Search', function($rootScope, $state, Auth, Me, Authorization, $sce, Search) {
  if (!$rootScope.user) {
    $rootScope.user = Me.get(function() {
      if (!$rootScope.user.avatar)
        $rootScope.user.avatar = 'files/user_profile_default.png';
      authorize();
    });
  } else {
    authorize();
  }

  $rootScope.logout = function() {
    var status = Auth.logout(function() {
      document.cookie = "sessionid=; expires=Thu, 01 Jan 1970 00:00:00 UTC";
      window.location.href = '/';
    });
  };

  function authorize() {
    $rootScope.$on('$stateChangeStart', function (event, next) {
      var authorised;
      if (next.access !== undefined) {
        if (Authorization.authorize(next.access))
          $state.go(next.name);
          // authorised = authorization.authorize(next.access.loginRequired, next.access.permissions, next.access.permissionCheckType);
          // if (authorised === jcs.modules.auth.enums.authorised.loginRequired) {
          //     $location.path(jcs.modules.auth.routes.login);
          // } else if (authorised === jcs.modules.auth.enums.authorised.notAuthorised) {
          //     $location.path(jcs.modules.auth.routes.notAuthorised).replace();
          // }
      }
    });
  }

  // Get the user's location
  function geo_success(position) {
    console.log(position);
    $rootScope.position = position;
  }

  function geo_error() {

  }

  var geo_options = {
    enableHighAccuracy: true,
    maximumAge: 30000,
    timeout: 27000
  };

  if ('geolocation' in navigator) {
    navigator.geolocation.getCurrentPosition(geo_success, geo_error);
    var wpid = navigator.geolocation.watchPosition(geo_success, geo_error, geo_options);
  }

  $rootScope.search = function(form, term) {
    if (form.$invalid) return;
    $rootScope.s.r = Search.query({term: term}, function() {
      // Loading indicator
    });
  };
}])

.service('Authorization', ['$rootScope', function($rootScope) {
  this.authorize = function(access) {
    if (access.permissionType === 'or') {
      for (var k in access.permissions) {
        if (check(access.permissions[k]))
          return;
      }
    }
  };

  function check(perm) {
    if (perm === 'BarOwner') {
      return ($rootScope.user.bar_owner === true);
    }
  }
}])

.directive('buyDrinks', ['$rootScope', function($rootScope) {
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
          scope.order.emails = [$rootScope.user.email];
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

.directive('focus', ['$timeout', function($timeout) {
  return {
    link: function(scope, element) {
      $timeout(function() {
        element[0].focus();
      }, 0);
    }
  };
}])

.factory('months', [function() {
  return {
    '01': 'January',
    '02': 'Febuary',
    '03': 'March',
    '04': 'April',
    '05': 'May',
    '06': 'June',
    '07': 'July',
    '08': 'August',
    '09': 'September',
    '10': 'October',
    '11': 'November',
    '12': 'December'
  };
}])

.filter('formatDate', [function() {
  return function(input) {
    console.log(input);
    return new Date(input).toLocaleString();
  };
}]);
