angular.module('App')

.controller('HomeCtrl', ['$scope', '$state', 'UserBars', 'Bartender', function($scope, $state, UserBars, Bartender) {
	$state.go('tabs-open.for');
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

.controller('TabOpenCtrl', ['$rootScope', '$scope', '$state', '$modal', 'UserSearch', 'Tab', 'Source', function($rootScope, $scope, $state, $modal, UserSearch, Tab, Source) {
	$scope.users = [];
	$scope.searching = false;
	$scope.term = '';
	$scope.buyingType = 'tab';
	$scope.tab = new Tab();
	$scope.tab.emails = [];
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
      $scope.tab.emails = [''];
    }
  };

	$scope.search = function(term) {
		$scope.users = UserSearch.query({term: term}, function() {
			$scope.searching = true;
		});
	};

	$scope.selectUser = function(user) {
		$scope.searching = false;
		$scope.order.emails[0] = user.email;
	};

	$scope.selectSource = function(source) {
		$scope.tab.source = source.id;
		$scope.selectedSource = source;
	};

	$scope.submit = function() {
		$scope.tab.email = $scope.tab.emails[0];
		$scope.tab.$save(function() {
			$state.go('tabs');
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

.controller('TabCtrl', ['$scope', '$modal', 'MyTab', 'Tab', function($scope, $modal, MyTab, Tab) {
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

	$scope.processPayment = function(form) {
		if (form.$invalid) return;

		$scope.processing = true;

		// setTimeout(function() {
		// 	$scope.processing = false;
		// 	$scope.$digest();
		// }, 1000);
	};
}])

.controller('UserProfileCtrl', ['$scope', 'Me', 'Source', function($scope, Me, Source) {
	$scope.user = Me.get();
	$scope.cards = Source.query();

	$scope.save = function(form, user) {
		if (form.$invalid) return;
		user.$save();
	};

	$scope.createNewCard = function(form, newcard) {
		if (form.$invalid) return;
		$scope.adding = true;

		Stripe.setPublishableKey(pk);

		Stripe.card.createToken({
      number: newcard.number,
      cvc: newcard.cvc,
      exp_month: (newcard.month.getMonth()>10)?'0'+newcard.month.getMonth():''+newcard.month.getMonth(),
      exp_year: newcard.year,
      currency: newcard.currency || 'usd'
    }, stripeResponseHandler);

    function stripeResponseHandler(status, response) {
	    var $form = form;
	    $scope.adding = false;

	    if (response.error) {
	      $scope.$digest();
	      // Show the errors on the form
	      // $form.find('.payment-errors').text(response.error.message);
	      // $form.find('button').prop('disabled', false);
	    } else {
	      // response contains id and card, which contains additional card details
	      var token = response.id;
	      $scope.newcard.stripe_token = token;
	      $scope.$digest();
	      var c = new Source();
	      c.token = token;
	      c.$save();
	      // element[0].submit();
	      // Insert the token into the form so it gets submitted to the server
	      // $form.append($('<input type="hidden" name="stripeToken" />').val(token));
	      // and submit
	      // $form.get(0).submit();
	    }
	  }
	};
}]);