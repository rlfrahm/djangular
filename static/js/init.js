angular.module('Init', ['ui.bootstrap'])

.config(['$interpolateProvider', function($interpolateProvider) {
  $interpolateProvider.startSymbol('{[{').endSymbol('}]}');
}])

.directive('fileModel', ['$parse', function($parse){
  return {
    restrict: 'A', // E = Element, A = Attribute, C = Class, M = Comment
    link: function(scope, element, attrs) {
      var model = $parse(attrs.fileModel),
        modelSetter = model.assign;

      element.bind('change', function() {
        scope.$apply(function() {
          modelSetter(scope, element[0].files[0]);
        });
      });
    }
  };
}])

.service('FileField', [function() {
  this.getURL = function(file, callback) {
    var fr = new FileReader();

    fr.onload = function(e) {
      if (callback) {
        callback(e);
      }
    };

    fr.readAsDataURL(file);
  };
}])

.directive('avatar', ['FileField', function(FileField) {
  return {
    link: function(scope, element, attrs) {
      var watch = attrs.avatar || 'avatar';
      // scope.avatarSRC = '/static/images/silhouette78.png';

      scope.$watch(watch, function(newval) {
        if (!newval) return;
        FileField.getURL(newval, function(e) {
          scope.avatarSRC = e.target.result;
          scope.$digest();
        });
      });
    }
  };
}])

.directive('createCardFormBody', [function() {
  return {
    templateUrl: '/static/partials/directives/create_card_form.html'
  };
}])

.directive('createCardForm', ['months', function(months) {
	return {
		link: function(scope, element, attrs) {
      Stripe.setPublishableKey(pk);

      scope.valid = {
        cardNumber: null,
        expiry: null,
        cvc: null,
        type: null
      };

			scope.months = months;
			scope.newcard = {
				month: '01'
			};

      element.on('submit', function(e) {
        e.preventDefault();
        createNewCard();
      });

			scope.setMonth = function(month) {
				scope.newcard.month = month;
        scope.validateExpiry(month, scope.newcard.year);
			};

      scope.validateCardNumber = function(number) {
        if (!number) return;
        scope.valid.cardNumber = Stripe.card.validateCardNumber(number);
        scope.valid.type = Stripe.card.cardType(number);
      };

      scope.validateExpiry = function(month, year) {
        if (!month || !year) return;
        scope.valid.expiry = Stripe.card.validateExpiry(month, year);
      };

      scope.validateCVC = function(cvc) {
        scope.valid.cvc = Stripe.card.validateCVC(cvc);
      };

			function createNewCard() {
				if (scope.form.$invalid) return;
				scope.form.loading = true;
        var form = scope.form,
          newcard = scope.newcard;

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
			      // Show the errors on the form
			      // $form.find('.payment-errors').text(response.error.message);
			      // $form.find('button').prop('disabled', false);
			    } else {
			      // response contains id and card, which contains additional card details
			      var token = response.id;
			      scope.newcard.token = token;
            console.log(scope.saveNewCard, scope);
            if (attrs.submit)
              element.submit();
            else if (scope.saveNewCard)
              scope.saveNewCard(token);
			      // var c = new Source();
			      // c.token = token;
			      // c.$save();
			    }
  				scope.form.loading = true;
			  }
			};
		}
	};
}])

.factory('months', [function() {
  return {
    '01': 'January',
    '02': 'Febuary',
    '03': 'March',
    '04': 'April',
    '05': 'May',
    '06': 'June',
    '07': 'July',
    '08': 'August',
    '09': 'September',
    '10': 'October',
    '11': 'November',
    '12': 'December'
  };
}]);
