angular.module('App')

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
}]);
