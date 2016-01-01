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
    .state('home', {
      url: '/',
      templateUrl: 'static/partials/home.html',
      controller: 'HomeCtrl'
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

  // if ('geolocation' in navigator) {
  //   navigator.geolocation.getCurrentPosition(geo_success, geo_error);
  //   var wpid = navigator.geolocation.watchPosition(geo_success, geo_error, geo_options);
  // }

  $rootScope.s = {};

  $rootScope.search = function(form, term) {
    if (form.$invalid) return;
    $rootScope.s.searching = true;
    $rootScope.s.r = Search.query({term: term}, function() {
      // Loading indicator
    });
  };

  $rootScope.cancelSearch = function() {
    $rootScope.s.searching = false;
    $rootScope.s.q = '';
  };

  $rootScope.isValidEmail = function(text) {
    var re = /^([\w-]+(?:\.[\w-]+)*)@((?:[\w-]+\.)*\w[\w-]{0,66})\.([a-z]{2,6}(?:\.[a-z]{2})?)$/i;
    return re.test(text);
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

.directive('focus', ['$timeout', function($timeout) {
  return {
    link: function(scope, element) {
      $timeout(function() {
        element[0].focus();
      }, 0);
    }
  };
}])

.filter('formatDate', [function() {
  return function(input) {
    console.log(input);
    return new Date(input).toLocaleString();
  };
}]);
