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

.directive('addressAutocomplete', ['$rootScope', '$parse', function($rootScope, $parse) {
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
				scope[attrs.model].geocoding = true;
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
				scope[attrs.model].geocoding = true;

				if (scope.locationChange) scope.locationChange();
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

.directive('buyDrinks', ['$rootScope', '$modal', 'BarPayment', 'BarSale', function($rootScope, $modal, BarPayment, BarSale) {
	return {
		link: function($scope, element, attrs) {
			$scope.payment = {};
			$scope.selectBar = function(bar) {
				$scope.payment.bar = bar;
				$scope.payment.barSearch = bar.name;
			};

			$scope.unselectBar = function() {
				$scope.payment.bar = null;
				$scope.payment.barSearch = '';
			}

			$scope.payForDrinkHere = function(bar) {
				if (!$rootScope.user.sources) {
					$scope.showNoPaymentSourcesModal();
					return;
				}

				$scope.payment.bar = bar;
		    $scope.showPayForDrinkBartenderModal();
			};

			$scope.barIsSelected = function() {
				return !!$scope.payment.bar;
			};

			$scope.showNoPaymentSourcesModal = function() {
				var m = $modal.open({
		      templateUrl: 'no-drink-sources.html',
		      scope: $scope
		    });
			};

			$scope.payForDrink = function(tab) {
				if (!$rootScope.user.sources) {
					$scope.showNoPaymentSourcesModal();
					return;
				}

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
				$scope.payment.status = '';
				var m = $modal.open({
		      templateUrl: 'pay-for-drink-bartender.html',
		      scope: $scope,
					backdrop: 'static'
		    });

		    m.result.then(function(email) {
		    });
			};

			$scope.payment.status = '';
			$scope.processPayment = function(form, close) {
				if (form.$invalid) return;

				$scope.loading = true;

		    var payment = new BarPayment();
		    payment.amount = $scope.payment.cost;
		    var p = payment.$save({id: $scope.payment.bar.id}, function(res) {
					$scope.loading = false;
					$scope.payment.status = 'success';
					$scope.payment.sale = res.sale;
					$scope.payment.transactions = res.transactions;
					$scope.payment.total = res.total;
					$scope.payment.tipPercent = 20;
					if ($scope.getMyTab)
						$scope.getMyTab();
				}, function(err) {
					console.log(err);
					$scope.payment.status = 'fail';
					$scope.loading = false;
				});
			};

			$scope.tryPaymentProcessAgain = function() {
				$scope.payment.status = '';
				$scope.loading = false;
			};

			$scope.showTipModal = function(close) {
				close();
				var m = $modal.open({
		      templateUrl: 'pay-for-drink-tip.html',
		      scope: $scope
		    });
				$scope.payment.status = '';
			};

			$scope.skipTip = function(dismiss) {
				dismiss();
				// $scope.showPaymentSummaryModal();
			};

			$scope.addToTip = function() {
				$scope.payment.tipPercent++;
			};

			$scope.removeFromTip = function() {
				if ($scope.payment.tipPercent > 1)
					$scope.payment.tipPercent--;
			};

			$scope.$watch('payment.tipPercent', function(newval) {
				if (!newval) return;
				$scope.tipChanged();
			});

			$scope.tipChanged = function() {
				if ($scope.payment.transactions[$scope.payment.transactions.length - 1].type == 'user') {
					// If the last transaction is using the user's source
					// add the tip to it
					$scope.payment.transactions[$scope.payment.transactions.length - 1].tip = $scope.getTotalTip();
				}
			};

			$scope.getTotalTip = function() {
				return $scope.payment.total * $scope.payment.tipPercent / 100;
			}

			$scope.getPaymentTotal = function() {
				return $scope.payment.total * (1 + ($scope.payment.tipPercent/100));
			};

			$scope.submitTip = function(form, close) {
				if (form.$invalid) return;

				$scope.loading = true;

				var bs = new BarSale();
				bs.tip = $scope.getTotalTip();
				console.log(bs);
				bs.$put({id: $scope.payment.bar.id, sid: $scope.payment.sale}, function(res) {
					console.log(res);
					$scope.payment.status = 'success';
					$scope.loading = false;
				}, function(err) {
					console.log(err);
					$scope.payment.status = 'fail';
					$scope.loading = false;
				});
				// close();
				// $scope.showPaymentSummaryModal();
			};

			$scope.closeTipModal = function(close) {
				close();
			};

			$scope.showPaymentSummaryModal = function() {
				var m = $modal.open({
		      templateUrl: 'pay-for-drink-summary.html',
		      scope: $scope
		    });
			};
		}
	};
}]);
