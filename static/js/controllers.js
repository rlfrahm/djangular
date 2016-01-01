'use strict'

angular.module('App')

.controller('HomeCtrl', ['$scope', '$state', 'Analytics', function($scope, $state, Analytics) {
	Analytics.pageview();
	$state.go('home');
}])

.controller('UserProfileCtrl', ['$rootScope', '$scope', '$http', '$modal', 'Me', 'MePassword', 'Source', 'UserAvatar', 'FileField', 'Analytics', 'toastr', function($rootScope, $scope, $http, $modal, Me, MePassword, Source, UserAvatar, FileField, Analytics, toastr) {
	Analytics.pageview('My Profile');

	$scope.loading = true;
  $scope.getCards = function() {
    $scope.cards = Source.query(function() {
			$scope.loading = false;
		});
  };

  $scope.getCards();

	$scope.saveUser = function(form, user) {
		if (form.$invalid) return;
		user.$save();
	};

	$scope.submitChangePassword = function(form, newpass, $close) {
		if (form.$invalid) return;
		newpass.$save();
		console.log($scope);
		toastr.success('Success!', 'Your password has been changed! Please use it the next time you login!');
		$close('saved');
	};

	$scope.openChangePasswordModal = function() {
		$scope.newpass = new MePassword();
		var m = $modal.open({
      templateUrl: 'change-password.html',
      size: 'sm',
      scope: $scope
    });

    m.result.then(function(email) {
    });
	};

  $scope.$watch('avatar', function(newval) {
    if (!newval) return;
    var fd = new FormData();
    fd.append('avatar', newval);

    FileField.getURL(newval, function(e) {
      $rootScope.user.avatar = e.target.result;
    });

    // console.log($scope.avatarSRC);
    // $rootScope.user.avatar = $scope.avatarSRC;

    // var ua = new UserAvatar();
    // ua.$save(fd);

    $http({
      method: 'POST',
      url: '/api/v1/user/avatar',
      data: fd,
      headers: {
        'Content-Type': undefined
      }
    });
  });

	$scope.setDefaultCard = function(card) {
		var source = new Source();
		source.$save({id: card.id}, function() {
			$scope.cards.forEach(function(c) {
				if (c.id == card.id)
					c.default_source = true;
				else
					c.default_source = false;
			});
		});
	};

	$scope.newCardDialog = function() {
		var s = $scope.$new();

		var m = $modal.open({
      templateUrl: 'credit-card-form.html',
      size: 'md',
      scope: s,
			controller: 'CreditCardFormController'
    });

    m.result.then(function(email) {
    });
	};
}])

.controller('UserHandler', ['$scope', '$stateParams', 'User', 'Time', 'Analytics', function($scope, $stateParams, User, Time, Analytics) {
	$scope.usr = User.get({id: $stateParams.id}, function() {
		Analytics.pageview($scope.usr.first_name + ' ' + $scope.usr.last_name);
		$scope.usr.checkins.forEach(function(e) {
			var t1 = new Date();
			e.when = Time.diff(t1, new Date(e.when));
		});
	});
}]);
