'use strict'

angular.module('App')

.controller('HomeCtrl', ['$scope', '$state', 'UserBars', 'Bartender', 'Analytics', function($scope, $state, UserBars, Bartender, Analytics) {
	Analytics.pageview();
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

.controller('BarsCtrl', ['$scope', 'Bars', 'Analytics', function($scope, Bars, Analytics) {
	Analytics.pageview('Bars');
	$scope.bars = Bars.query();
}])

.controller('UserBarsCtrl', ['$scope', '$state', 'UserBars', 'Analytics', function($scope, $state, UserBars, Analytics) {
	Analytics.pageview('My Bars');
	$scope.bars = UserBars.query(function() {

	});
}])

.controller('BarCtrl', ['$scope', '$state', '$stateParams', 'Bar', 'Bartenders', 'Checkin', 'Time', 'Analytics', function($scope, $state, $stateParams, Bar, Bartenders, Checkin, Time, Analytics) {
	$scope.bar = Bar.get({id: $stateParams.id}, function() {
		Analytics.pageview($scope.bar.name);
    var map = new google.maps.Map(document.getElementById('map'), {
      center: {lat: $scope.bar.lat, lng: $scope.bar.lng},
      zoom: 16,
      draggable: false,
      scrollwheel: false
    });

    var marker = new google.maps.Marker({
	    position: new google.maps.LatLng($scope.bar.lat, $scope.bar.lng),
	    map: map,
	    title: $scope.bar.name,
    	animation: google.maps.Animation.DROP
	  });
  });
	$scope.bartenders = Bartenders.query({id: $stateParams.id});

	$scope.checkin = function() {
		var checkin = new Checkin();
		checkin.$save({id: $scope.bar.id}, getCheckins);
	};

	function getCheckins() {
		$scope.checkins = Checkin.query({id: $stateParams.id}, function() {
			var t1 = new Date();
			$scope.checkins.forEach(function(e) {
				e.when = Time.diff(t1, new Date(e.when));
			});
		});
	}
	getCheckins();
}])

.controller('BarAddCtrl', ['$scope', '$state', 'Bar', 'Analytics', function($scope, $state, Bar, Analytics) {
	Analytics.pageview('Register Bar');
	$scope.newbar = new Bar();

	$scope.avatarSRC = '/static/images/user_profile_default.png';

	$scope.create = function() {
		if ($scope.newbar.avatarFile){
			var fd = new FormData();
			fd.append('avatar', $scope.newbar.avatarFile);
			$scope.newbar.avatar = fd;
		}

		$scope.newbar.$save(function() {
			$state.go('bars-mine');
		});
	};
}])

.controller('BarSettingsCtrl', ['$rootScope', '$scope', '$state', '$stateParams', '$modal', '$http', 'Bar', 'Bartenders', 'UserSearch', 'Analytics', function($rootScope, $scope, $state, $stateParams, $modal, $http, Bar, Bartenders, UserSearch, Analytics) {
	$scope.bar = Bar.get({id: $stateParams.id}, function() {
		Analytics.pageview($scope.bar.name + ' Settings');
    if ($scope.bar.street && $scope.bar.postal)
      $scope.bar.address = $scope.bar.street + ', ' + $scope.bar.city + ', ' + $scope.bar.province + ' ' + $scope.bar.postal;
		$scope.avatarSRC = $scope.bar.avatar;
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

	$scope.$watch('bar.avatarFile', function(newval) {
    if (!newval) return;
    var fd = new FormData();
    fd.append('avatar', newval);

		console.log(newval);

    $http({
      method: 'POST',
      url: '/api/v1/bars/' + $scope.bar.id + '/avatar',
      data: fd,
      headers: {
        'Content-Type': undefined
      }
    });
  });
}])

.controller('TabOpenCtrl', ['$rootScope', '$scope', '$state', '$stateParams', '$modal', 'UserSearch', 'Tab', 'Source', 'Analytics', function($rootScope, $scope, $state, $stateParams, $modal, UserSearch, Tab, Source, Analytics) {
	Analytics.pageview('Open A Tab');
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

.controller('TabCtrl', ['$scope', '$modal', 'MyTab', 'Tab', 'BarPayment', 'Analytics', function($scope, $modal, MyTab, Tab, BarPayment, Analytics) {
	Analytics.pageview('My Tab');
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

.controller('UserProfileCtrl', ['$rootScope', '$scope', '$http', '$modal', 'Me', 'MePassword', 'Source', 'UserAvatar', 'FileField', 'Analytics', function($rootScope, $scope, $http, $modal, Me, MePassword, Source, UserAvatar, FileField, Analytics) {
	Analytics.pageview('My Profile');
	// $rootScope.user = Me.get(function() {
 //  });
	// var clear = $rootScope.$watch('user.avatar', function(newval) {
	// 	if (!newval) return;
	// 	// $scope.avatarSRC = $rootScope.user.avatar;
	// 	clear();
	// });

  $scope.getCards = function() {
    $scope.cards = Source.query();
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
