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
}]);;