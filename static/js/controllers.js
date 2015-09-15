angular.module('App')

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

.controller('BarSettingsCtrl', ['$scope', '$stateParams', 'Bar', function($scope, $stateParams, Bar) {
	$scope.bar = Bar.get({id: $stateParams.id});
}]);