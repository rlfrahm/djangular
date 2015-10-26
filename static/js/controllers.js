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

.controller('BarsCtrl', ['$rootScope', '$scope', 'Bars', 'Analytics', 'buildAddress', function($rootScope, $scope, Bars, Analytics, buildAddress) {
	Analytics.pageview('Bars');
	var markers = [];

	var mapUpdate = {
		bounds: false,
		dragend: false
	};

	$scope.address = function(bar) {
		return buildAddress(bar);
	};

	var coords = {lat: null, lng: null};

	// $rootScope.map = new google.maps.Map(document.getElementById('map'), {
	// 	zoom: 16
	// });
	//
	// $scope.initMap = function() {
	// 	var watcher = $rootScope.$watch('position.coords', function(newval) {
	// 		if (!newval) return;
	//
	// 		coords.lat = newval.latitude;
	// 		coords.lng = newval.longitude;
	//
	// 		$rootScope.map.setCenter(coords);
	// 		mapUpdate.dragend = true;
	// 		watcher();
	// 	});
	// };
	//
	// google.maps.event.addListener($rootScope.map, 'bounds_changed', function() {
	// 	mapUpdate.bounds = true;
	//  	updateMap();
  // });
	//
	// google.maps.event.addListener($rootScope.map, 'dragend', function() {
	// 	mapUpdate.dragend = true;
	//  	updateMap();
  // });
	//
	// function updateMap() {
	// 	if (!mapUpdate.bounds && !mapUpdate.dragend) return;
	// 	var mapBounds = $rootScope.map.getBounds();
	// 	console.log(mapBounds, coords, $rootScope.map.getBounds());
	// 	var distance = google.maps.geometry.spherical.computeDistanceBetween(mapBounds.getNorthEast(), mapBounds.getSouthWest()) / 2;
	// 	console.log(distance);
	// 	getBars(distance, coords.lat, coords.lng);
	// 	mapUpdate.bounds = false;
	// 	mapUpdate.dragend = false;
	// }

	getBars();

	function getBars(distance, lat, lng) {
		var q = {};
		if (distance && lat && lng) {
			q = {
				distance: distance,
				lat: lat,
				lng: lng
			};
		}
		$scope.bars = Bars.query(q, function() {
			$scope.bars.forEach(function(b) {
				markers.push(new google.maps.Marker({
					position: new google.maps.LatLng(b.lat, b.lng),
					title: b.name,
					map: $rootScope.map
				}));
			});
		});
	}
}])

.controller('UserBarsCtrl', ['$scope', '$state', 'UserBars', 'Analytics', function($scope, $state, UserBars, Analytics) {
	Analytics.pageview('My Bars');
	$scope.bars = UserBars.query(function() {

	});
}])

.controller('BarCtrl', ['$rootScope', '$scope', '$state', '$stateParams', 'Bar', 'Bartenders', 'Checkin', 'Time', 'Analytics', function($rootScope, $scope, $state, $stateParams, Bar, Bartenders, Checkin, Time, Analytics) {
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

		$scope.newbar.$save(function(res) {
			console.log(res);
			$state.go('bar-settings.general', {id: res.id});
		});
	};
}])

.controller('BarSettingsCtrl', ['$rootScope', '$scope', '$state', '$stateParams', '$modal', '$http', 'Bar', 'Bartenders', 'UserSearch', 'Analytics', 'BarSale', 'buildAddress', function($rootScope, $scope, $state, $stateParams, $modal, $http, Bar, Bartenders, UserSearch, Analytics, BarSale, buildAddress) {
	$scope.bar = Bar.get({id: $stateParams.id}, function() {
		Analytics.pageview($scope.bar.name + ' Settings');
    if ($scope.bar.street && $scope.bar.postal)
      $scope.bar.address = buildAddress($scope.bar);
		$scope.avatarSRC = $scope.bar.avatar;
  });
  $scope.search = {term:null};

	$scope.sales = BarSale.query({id: $stateParams.id});

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

	$scope.locationChange = function() {
		console.log($scope.bar);
		submitSave();
	};

	$scope.save = function(form) {
		if (form.$invalid || !$scope.shouldSave) return;
		submitSave();
	};

	function submitSave() {
		console.log($scope.bar);
		$scope.bar.$save({id: $scope.bar.id}, function() {
			$scope.bar.address = buildAddress($scope.bar);
		});
		$scope.shouldSave = false;
	}

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

.controller('TabOpenCtrl', ['$rootScope', '$scope', '$state', '$stateParams', '$modal', '$location', 'toastr', 'UserSearch', 'Tab', 'Source', 'Analytics', 'User', function($rootScope, $scope, $state, $stateParams, $modal, $location, toastr, UserSearch, Tab, Source, Analytics, User) {
	Analytics.pageview('Open A Tab');
	$scope.users = [];
	$scope.searching = false;
	$scope.term = '';
	$scope.buyingType = 'tab';
	$scope.tab = {};
	$scope.tab.users = [];
	console.log($location.search().id);
  if ($location.search().id) {
		var u = User.get({id: $location.search().id}, function() {
			$scope.tab.users.push(u);
		});
	}

	$scope.tab.amount = 20;
	$scope.tab.total = 0;
	$scope.selectedSource = null;

	$scope.order = {
    bar: '',
    bartender: '',
    users: [],
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

  $scope.setType = function(t) {
    $scope.tab.type = t;
    if (t == 'me') {
      $scope.tab.users = [$rootScope.user];
    } else {
      $scope.tab.users = [];
    }
  };

	$scope.search = function(term) {
		$scope.users = UserSearch.query({term: term}, function() {
			$scope.searching = true;
		});
	};

	$scope.selectUser = function(user) {
		if ($scope.tab.users.indexOf(user) > -1) return;
		$scope.searching = false;
		$scope.tab.users.push(user);
		$scope.term = '';
		$scope.total();
	};

	$scope.total = function() {
		$scope.tab.total = $scope.tab.users.length * $scope.tab.amount;
	};

	$scope.removeUser = function($index) {
		$scope.tab.users.splice($index, 1);
		$scope.total();
	};

	$scope.selectSource = function(source) {
		$scope.tab.source = source.id;
		$scope.selectedSource = source;
	};

	$scope.$watch('sources', function(newval) {
		if (!newval) return;

		$scope.tab.source = newval[0].id;
		$scope.selectedSource = newval[0];
	});

	$scope.loading = false;
	$scope.submit = function() {
		$scope.loading = true;
		var t = new Tab();
		t.users = [];
		$scope.tab.users.forEach(function(user) {
			if (user.id)
				t.users.push({id:user.id});
			else
				t.users.push({email:user.email});
		});
		t.amount = $scope.tab.amount;
		t.source = $scope.tab.source;
		if ($scope.tab.note)
			t.note = $scope.tab.note;

		t.$save(function() {
			$scope.loading = false;
			if ($scope.tab.users.length > 1)
				toastr.success('Tabs successfully created!', 'The users have been notified.');
			else
			 	toastr.success('Tab successfully created for ' + $scope.tab.users[0].first_name, 'They have been notified');
			$state.go('tab');
		});
	};

  $scope.addNewPaymentMethod = function() {
    var m = $modal.open({
      templateUrl: 'select-payment-method.html',
    });

    m.result.then(function(email) {
    });
  };

	$scope.filterOutUserRepeats = function(user) {
		return ($scope.tab.users.indexOf(user) < 0);
	};
}])

.controller('TabCtrl', ['$scope', '$modal', 'MyTab', 'Tab', 'BarPayment', 'Analytics', function($scope, $modal, MyTab, Tab, BarPayment, Analytics) {
	Analytics.pageview('My Tab');
  $scope.title = 'Tab';
	$scope.tabs = Tab.query();

	var t;
	$scope.getMyTab = function() {
		t = MyTab.get(function() {
			$scope.tab = t.tab;
		});
	}
	$scope.getMyTab();

	$scope.loading = false;

	$scope.confirmTab = function(tab, decision, close) {
		$scope.loading = true;
		tab.accepted = decision;
		t = angular.copy(tab);
		t.$save({id: tab.id}, function() {
			if (!t.accepted)
				$scope.tabs.splice($scope.tabs.indexOf(tab), 1);
			else
				$scope.getMyTab();
			close();
			$scope.loading = false;
		});
	};

	$scope.showTabModal = function(tab) {
		var s = $scope.$new();
		s.tab = tab;
    var m = $modal.open({
      templateUrl: 'tab-detail.html',
      scope: s
    });

    m.result.then(function(email) {
    });
  };
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

	$scope.saveNewCard = function(token) {
		var source = new Source();
		source.token = token;
		source.$save(function() {
			toastr.success('Success!', 'Your card has been added!');
			$scope.getCards();
			$rootScope.user.sources = true;
		});
	};

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
      size: 'sm',
      scope: s
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
