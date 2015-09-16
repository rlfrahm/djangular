angular.module('App')

.controller('BarsCtrl', ['$scope', 'Bars', function($scope, Bars) {
	$scope.bars = Bars.query();
}])

.controller('UserBarsCtrl', ['$scope', '$state', 'UserBars', function($scope, $state, UserBars) {
	$scope.bars = UserBars.query(function() {

	});
}])

.controller('BarCtrl', ['$scope', '$state', '$stateParams', 'Bar', function($scope, $state, $stateParams, Bar) {
	$scope.bar = Bar.get({id: $stateParams.id});
}])

.controller('BarAddCtrl', ['$scope', '$state', 'Bar', function($scope, $state, Bar) {
	$scope.newbar = new Bar();

	$scope.create = function() {
		$scope.newbar.$save(function() {
			$state.go('bars-mine');
		});
	};
}])

.controller('BarSettingsCtrl', ['$rootScope', '$scope', '$state', '$stateParams', '$modal', 'Bar', 'Bartenders', function($rootScope, $scope, $state, $stateParams, $modal, Bar, Bartenders) {
	$scope.bar = Bar.get({id: $stateParams.id});
	$scope.bartenders = Bartenders.query({id: $stateParams.id});
	$scope.shouldSave = false;

	$scope.isState = function(s) {
		return $state.is(s);
	};

	$scope.changed = function() {
		$scope.shouldSave = true;
	};

	$scope.save = function(form) {
		if (form.$invalid || !$scope.shouldSave) return;

		$scope.bar.$save();
		$scope.shouldSave = false;
	};

	$scope.confirmDelete = function() {
		var m = $modal.open({
			templateUrl: 'confirm-delete.html',
			size: 'sm'
		});

		m.result.then(function(username) {
			if (username == $rootScope.user.username) {
				console.log($scope.bar);
				$scope.bar.$delete(function() {
					$state.go('bars-mine');
				});
			}
		});
	};

	$scope.inviteBartender = function() {
		var m = $modal.open({
			templateUrl: 'invite-bartender.html',
			size: 'sm'
		});

		m.result.then(function(username) {
			if (username == $rootScope.user.username) {
				console.log($scope.bar);
				$scope.bar.$delete(function() {
					$state.go('bars-mine');
				});
			}
		});
	};
}]);