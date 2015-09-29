'use strict'

angular.module('App')

.controller('HomeCtrl', ['$scope', '$state', 'UserBars', 'Bartender', function($scope, $state, UserBars, Bartender) {
	$state.go('tab');
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
	$scope.bar = Bar.get({id: $stateParams.id}, function() {
    var map = new google.maps.Map(document.getElementById('map'), {
      center: {lat: $scope.bar.lat, lng: $scope.bar.lng},
      zoom: 8,
      draggable: false,
      scrollwheel: false
    });
  });
	$scope.bartenders = Bartenders.query({id: $stateParams.id});
	$scope.checkins = Checkin.query({id: $stateParams.id});

	$scope.checkin = function() {
		var checkin = new Checkin();
		checkin.$save({id: $scope.bar.id});
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

.controller('BarSettingsCtrl', ['$rootScope', '$scope', '$state', '$stateParams', '$modal', 'Bar', 'Bartenders', 'UserSearch', function($rootScope, $scope, $state, $stateParams, $modal, Bar, Bartenders, UserSearch) {
	$scope.bar = Bar.get({id: $stateParams.id}, function() {
    if ($scope.bar.street && $scope.bar.postal)
      $scope.bar.address = $scope.bar.street + ', ' + $scope.bar.city + ', ' + $scope.bar.province + ' ' + $scope.bar.postal;
  });
  $scope.search = {term:null};
	
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

  $scope.search = function(term) {
    $scope.users = UserSearch.query({term: term}, function() {
      $scope.searching = true;
    });
  };

  $scope.selectUser = function(u) {
    $scope.search.term = (u.first_name)?u.first_name + ' ' + u.last_name:u.email;
    $scope.invite = u;
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
			size: 'sm',
      scope: $scope
		});

		m.result.then(function(user) {
      console.log(user);
			var bartender = new Bartenders();
			bartender.email = user.email;
			bartender.$save({id: $stateParams.id});
		});
	};
}])

.controller('TabOpenCtrl', ['$rootScope', '$scope', '$state', '$stateParams', '$modal', 'UserSearch', 'Tab', 'Source', function($rootScope, $scope, $state, $stateParams, $modal, UserSearch, Tab, Source) {
	$scope.users = [];
	$scope.searching = false;
	$scope.term = '';
	$scope.buyingType = 'tab';
	$scope.tab = new Tab();
	$scope.tab.emails = [];
  if ($stateParams.for)
    $scope.tab.emails.push($stateParams.for);
	$scope.tab.amount = 10;
	$scope.selectedSource = null;

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
    if (t == 'me') {
      $scope.tab.emails = [$rootScope.user.email];
    } else {
      $scope.tab.emails = [];
    }
  };

	$scope.search = function(term) {
		$scope.users = UserSearch.query({term: term}, function() {
			$scope.searching = true;
		});
	};

	$scope.selectUser = function(user) {
		$scope.searching = false;
		$scope.tab.emails.push(user.email);
	};

	$scope.selectSource = function(source) {
		$scope.tab.source = source.id;
		$scope.selectedSource = source;
	};

	$scope.submit = function() {
		$scope.tab.email = $scope.tab.emails[0];
		$scope.tab.$save(function() {
			$state.go('tab');
		});
	};

  $scope.addNewPaymentMethod = function() {
    var m = $modal.open({
      templateUrl: 'select-payment-method.html',
      size: 'sm'
    });

    m.result.then(function(email) {
    });
  };
}])

.controller('TabCtrl', ['$scope', '$modal', 'MyTab', 'Tab', 'BarPayment', function($scope, $modal, MyTab, Tab, BarPayment) {
  $scope.title = 'Tab';
	$scope.tabs = Tab.query()
	var t = MyTab.get(function() {
		$scope.tab = t.tab;
	});

	$scope.selectBar = function(bar) {
		$scope.term = bar.name;
		$scope.bar = bar;
	};

	$scope.useTab = function(tab) {
    var m = $modal.open({
      templateUrl: 'tab-checkout.html',
      size: 'sm',
      scope: $scope
    });

    m.result.then(function(email) {
    });
	};

	$scope.processPayment = function(form, bar_id, amount) {
		if (form.$invalid) return;

		$scope.processing = true;

    var payment = new BarPayment();
    payment.amount = amount;
    var p = payment.$save({id: bar_id});
	};

	$scope.confirmTab = function(tab, decision) {
		tab.accepted = decision;
		tab.$save({id: tab.id});
		$scope.$close();
	};

	$scope.showTabModal = function(tab) {
		var s = $scope.$new();
		s.tab = tab;
    var m = $modal.open({
      templateUrl: 'tab-detail.html',
      size: 'sm',
      scope: s
    });

    m.result.then(function(email) {
    });
  };
}])

.controller('UserProfileCtrl', ['$scope', '$http', 'Me', 'Source', 'UserAvatar', function($scope, $http, Me, Source, UserAvatar) {
	$scope.user = Me.get(function() {
    $scope.avatarSRC = $scope.user.avatar;
  });

  $scope.getCards = function() {
    $scope.cards = Source.query();
  };

  $scope.getCards();

	$scope.saveUser = function(form, user) {
		if (form.$invalid) return;
		user.$save();
	};

  $scope.$watch('avatar', function(newval) {
    if (!newval) return;
    var fd = new FormData();
    fd.append('avatar', newval);

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
}])

.controller('UserHandler', ['$scope', '$stateParams', 'User', function($scope, $stateParams, User) {
	$scope.usr = User.get({id: $stateParams.id});
}]);