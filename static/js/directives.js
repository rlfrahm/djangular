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

.directive('createCardForm', ['months', 'Source', function(months, Source) {
	return {
		// templateUrl: '/static/partials/directives/create_card_form.html',
		link: function(scope, element, attrs) {
			scope.months = months;
			scope.newcard = {
				month: '01'
			};
			scope.setMonth = function(month) {
				$scope.newcard.month = month;
			};
			scope.createNewCard = function(form, newcard) {
				if (form.$invalid) return;
				scope.adding = true;

				Stripe.setPublishableKey(pk);

				Stripe.card.createToken({
		      number: newcard.number,
		      cvc: newcard.cvc,
		      exp_month: newcard.month,
		      exp_year: newcard.year,
		      currency: newcard.currency || 'usd'
		    }, stripeResponseHandler);

		    function stripeResponseHandler(status, response) {
			    var $form = form;
			    scope.adding = false;

			    if (response.error) {
			      scope.$digest();
			      // Show the errors on the form
			      // $form.find('.payment-errors').text(response.error.message);
			      // $form.find('button').prop('disabled', false);
			    } else {
			      // response contains id and card, which contains additional card details
			      var token = response.id;
			      scope.newcard.stripe_token = token;
			      scope.$digest();
			      var c = new Source();
			      c.token = token;
			      c.$save();
			      if (scope.getCards)
			      	scope.getCards();
			      // element[0].submit();
			      // Insert the token into the form so it gets submitted to the server
			      // $form.append($('<input type="hidden" name="stripeToken" />').val(token));
			      // and submit
			      // $form.get(0).submit();
			    }
			  }
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
}]);