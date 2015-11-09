angular.module('App')

.controller('CreditCardFormController', ['$rootScope', '$scope', 'Source', 'toastr', function($rootScope, $scope, Source, toastr) {
	$scope.saveNewCard = function(token) {
		var source = new Source();
		source.token = token;
		source.$save(function(res) {
			toastr.success('Success!', 'Your card has been added!');
			$scope.getCards();
			$rootScope.user.sources = true;
			$scope.loading = false;
			$scope.$close();
		}, function(res) {
			if (res.status == 400) {
				$scope.form.error = res.data.message;
			} else {
				$scope.form.error = 'An error has occurred';
			}
			$scope.loading = false;
		});
	};
}])
