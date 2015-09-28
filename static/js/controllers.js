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

  $scope.formatDate = function(string) {
    return new Date(string).toLocaleString();
  };

	$scope.checkin = function() {
		var checkin = new Checkin();
		checkin.$save({id: $scope.bar.id});
	};
}])

.controller('BarAddCtrl', ['$scope', '$state', 'Bar', function($scope, $state, Bar) {
	$scope.newbar = new Bar();

  var autocomplete, placeSearch;
  var componentForm = {
    street_number: 'short_name',
    route: 'long_name',
    locality: 'long_name',
    administrative_area_level_1: 'short_name',
    country: 'short_name',
    postal_code: 'short_name'
  }, tmp = {};

  autocomplete = new google.maps.places.Autocomplete(
    /** @type {!HTMLInputElement} */(document.getElementById('autocomplete')),
    {types: ['geocode']});

  autocomplete.addListener('place_changed', fillInAddress);

  function fillInAddress() {
    // Get the place details from the autocomplete object.
    var place = autocomplete.getPlace();

    // Get each component of the address from the place details
    // and fill the corresponding field on the form.
    for (var i = 0; i < place.address_components.length; i++) {
      var addressType = place.address_components[i].types[0];
      if (componentForm[addressType]) {
        var val = place.address_components[i][componentForm[addressType]];
        tmp[addressType] = val;
      }
    }

    $scope.newbar.street = tmp.street_number + ' ' + tmp.route;
    $scope.newbar.city = tmp.locality;
    $scope.newbar.province = tmp.administrative_area_level_1;
    $scope.newbar.postal = tmp.postal_code;
    $scope.newbar.country = tmp.country;
    console.log(place);
    $scope.newbar.lat = place.geometry.location.lat();
    $scope.newbar.lng = place.geometry.location.lng();
    console.log($scope.newbar);
  }

  // Bias the autocomplete object to the user's geographical location,
  // as supplied by the browser's 'navigator.geolocation' object.
  function geolocate() {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(function(position) {
        var geolocation = {
          lat: position.coords.latitude,
          lng: position.coords.longitude
        };
        var circle = new google.maps.Circle({
          center: geolocation,
          radius: position.coords.accuracy
        });
        autocomplete.setBounds(circle.getBounds());
      });
    }
  }

	$scope.create = function() {
		$scope.newbar.$save(function() {
			$state.go('bars-mine');
		});
	};
}])

.controller('BarSettingsCtrl', ['$rootScope', '$scope', '$state', '$stateParams', '$modal', 'Bar', 'Bartenders', 'UserSearch', function($rootScope, $scope, $state, $stateParams, $modal, Bar, Bartenders, UserSearch) {
	$scope.bar = Bar.get({id: $stateParams.id});
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

.controller('UserProfileCtrl', ['$scope', 'Me', 'Source', function($scope, Me, Source) {
	$scope.user = Me.get();

  $scope.getCards = function() {
    $scope.cards = Source.query();
  };

  $scope.getCards();

	$scope.saveUser = function(form, user) {
		if (form.$invalid) return;
		user.$save();
	};
}])

.controller('UserHandler', ['$scope', '$stateParams', 'User', function($scope, $stateParams, User) {
	$scope.usr = User.get({id: $stateParams.id});
}]);