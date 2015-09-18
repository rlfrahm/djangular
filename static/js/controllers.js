angular.module('App')

.controller('HomeCtrl', ['$scope', 'UserBars', 'Bartender', function($scope, UserBars, Bartender) {
	$scope.bars = UserBars.query();

	$scope.imWorking = function(bar) {
		var b = new Bartender();
		b.working = !bar.working;
		var res = b.$working({id: bar.id, bid: bar.bartender_id})
		.then(function(res) {
			bar.working = res.working;
		});
	};
}])

.controller('BarsCtrl', ['$scope', 'Bars', function($scope, Bars) {
	$scope.bars = Bars.query();
}])

.controller('UserBarsCtrl', ['$scope', '$state', 'UserBars', function($scope, $state, UserBars) {
	$scope.bars = UserBars.query(function() {

	});
}])

.controller('BarCtrl', ['$scope', '$state', '$stateParams', 'Bar', 'Bartenders', 'Checkin', function($scope, $state, $stateParams, Bar, Bartenders, Checkin) {
	$scope.bar = Bar.get({id: $stateParams.id});
	$scope.bartenders = Bartenders.query({id: $stateParams.id});
	$scope.checkins = Checkin.query({id: $stateParams.id});

	$scope.checkin = function() {
		var checkin = new Checkin();
		checking.$save({id: $scope.bar.id});
	};
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
	
	$scope.shouldSave = false;

	function refreshBartenders() {
		$scope.bartenders = Bartenders.query({id: $stateParams.id});	
	}

	refreshBartenders();

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

		m.result.then(function(email) {
			var bartender = new Bartenders();
			bartender.email = email;
			bartender.$save({id: $stateParams.id});
			// $scope.bartenders.$save();
		});
	};
}])

.controller('TabOpenCtrl', ['$rootScope', '$scope', '$state', 'UserSearch', 'Tab', function($rootScope, $scope, $state, UserSearch, Tab) {
	$scope.users = [];
	$scope.searching = false;
	$scope.term = '';
	$scope.buyingType = 'tab';
	$scope.tab = new Tab();
	$scope.tab.emails = [];

	$scope.order = {
    bar: '',
    bartender: '',
    emails: [],
    drinks: [
      { name: 'Beer', cost: 5 }
    ],
    title: ''
  };
  $scope.state = 0;
  $scope.setState = function(s) {
    $scope.state = s;
  };
  $scope.isState = function(s) {
    return (s == $scope.state);
  };
  $scope.addAnotherEmail = function() {
    if ($scope.tab.emails[$scope.tab.emails.length - 1] != '')
      $scope.tab.emails.push('');
  };
  $scope.setType = function(t) {
    $scope.tab.type = t;
    console.log(t);
    if (t == 'me') {
      $scope.tab.emails = [$rootScope.user.email];
    } else {
      $scope.tab.emails = [''];
    }
  };

	$scope.search = function(term) {
		console.log(term);
		$scope.users = UserSearch.query({term: term}, function() {
			$scope.searching = true;
			console.log($scope.users);
		});
	};

	$scope.selectUser = function(user) {
		console.log(user);
		$scope.searching = false;
		$scope.order.emails[0] = user.email;
		console.log($scope.term);
	};

	$scope.submit = function() {
		$scope.tab.email = $scope.tab.emails[0];
		$scope.tab.$save(function() {
			$state.go('tabs');
		});
	};
}])

.controller('TabsCtrl', ['$scope', 'Tab', function($scope, Tab) {
	$scope.tabs = Tab.query()
}])

.controller('UserProfileCtrl', ['$scope', 'Me', function($scope, Me) {
	$scope.user = Me.get();

	$scope.save = function(form, user) {
		if (form.$invalid) return;
		console.log(user);
		user.$save();
	};
}]);