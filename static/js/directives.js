angular.module('App')

.directive('paymentSource', ['Source', function(Source){
	return {
		link: function(scope) {
			scope.sources = Source.query();
		}
	};
}])

.directive('barSearch', ['BarSearch', function(BarSearch) {
	return {
		link: function(scope) {
			scope.searchForBar = function(term) {
				scope.barslist = BarSearch.query({term: term}, function() {
					return scope.barslist;
				});
			};
		}
	};
}])

.directive('maxLength', [function(){
	return {
		link: function(scope, element, attrs) {
			scope.maxLength = attrs.maxLength;

			scope.calc = function(text) {
				scope.length = text.length;
			};

		}
	};
}])

.directive('googleMap', [function() {
	return {
		template: '<iframe width="100%" height="450" frameborder="0" style="border:0" ng-src="https://www.google.com/maps/embed/v1/place?q={[{bar.street}]},{[{bar.city}]},{[{bar.province}]}&key=AIzaSyAyJXdPAlRBVqqTqgrWodd11IqCg_-J68w" allowfullscreen></iframe>'
	};
}])

.directive('addressAutocomplete', ['$parse', function($parse) {
	return {
		link: function(scope, element, attrs) {
			var model = $parse(attrs.model),
        modelSetter = model.assign;

      // console.log(scope[attrs.model]);

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

		    scope[attrs.model].address = place.formatted_address;
		    scope[attrs.model].street = tmp.street_number + ' ' + tmp.route;
		    scope[attrs.model].city = tmp.locality;
		    scope[attrs.model].province = tmp.administrative_area_level_1;
		    scope[attrs.model].postal = tmp.postal_code;
		    scope[attrs.model].country = tmp.country;
		    scope[attrs.model].lat = place.geometry.location.lat();
		    scope[attrs.model].lng = place.geometry.location.lng();

		    // scope.$apply(function() {
      //     modelSetter(scope, obj);
      //     console.log(scope);
      //   });
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
		}
	};
}])

.directive('loader', [function() {
	return {
		restrict: 'E',
		template: '<div ng-if="loading"><i class="fa fa-spinner fa-pulse fa-3x"></i></div>'
	};
}])

.directive('buyDrinks', ['$modal', 'BarPayment', function($modal, BarPayment) {
	return {
		link: function($scope, element, attrs) {
			$scope.payment = {};
			$scope.selectBar = function(bar) {
				$scope.payment.bar = bar;
			};

			$scope.payForDrinkHere = function(bar) {
				$scope.payment.bar = bar;
		    $scope.showPayForDrinkBartenderModal();
			};

			$scope.payForDrink = function(tab) {
		    var m = $modal.open({
		      templateUrl: 'pay-for-drink-where.html',
		      scope: $scope
		    });

		    m.result.then(function(email) {
		    });
			};

			$scope.submitBar = function(form, close) {
				if (form.$invalid) return;
				close();

				$scope.showPayForDrinkBartenderModal();
			};

			$scope.showPayForDrinkBartenderModal = function() {
				var m = $modal.open({
		      templateUrl: 'pay-for-drink-bartender.html',
		      scope: $scope
		    });

		    m.result.then(function(email) {
		    });
			};

			$scope.processPayment = function(form, close) {
				if (form.$invalid) return;

				$scope.loading = true;

				// TEMPORARY OVERRIDE
				$scope.showTipModal(payment);
				close();
				$scope.loading = false;
				return;

		    var payment = new BarPayment();
		    payment.amount = $scope.payment.cost;
		    var p = payment.$save({id: bar_id}, function() {
					$scope.loading = false;
					close();
					$scope.showTipModal(payment);
				});
			};

			$scope.showTipModal = function(payment) {
				var m = $modal.open({
		      templateUrl: 'pay-for-drink-tip.html',
		      scope: $scope
		    });
			};
		}
	};
}]);
