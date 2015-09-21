angular.module('Api', ['ngResource'])

.factory('User', ['$resource', function($resource) {
	return $resource('/api/v1/users/:id');
}])

.factory('UserBars', ['$resource', function($resource) {
	return $resource('/api/v1/user/bars');
}])

.factory('Me', ['$resource', function($resource) {
	return $resource('/api/v1/user');
}])

.factory('MyTab', ['$resource', function($resource){
	return $resource('/api/v1/user/tab');
}])

.factory('Bar', ['$resource', function($resource) {
	return $resource('/api/v1/bars/:id');
}])

.factory('Checkin', ['$resource', function($resource) {
	return $resource('/api/v1/bars/:id/checkin')
}])

.factory('Bartender', ['$resource', function($resource) {
	return $resource('/api/v1/bars/:id/bartenders/:bid', {}, {
		working: {
			method: 'PUT'
		}
	});
}])

.factory('Bartenders', ['$resource', function($resource) {
	return $resource('/api/v1/bars/:id/bartenders', {}, {
		invite: {
			method: 'POST'
		}
	});
}])

.factory('Bars', ['$resource', function($resource) {
	return $resource('/api/v1/bars');
}])

.factory('Auth', ['$resource', function($resource) {
	return $resource('/api/v1/auth', {}, {
		logout: {
			method: 'DELETE'
		}
	});
}])

.factory('UserSearch', ['$resource', function($resource) {
	return $resource('/api/v1/search/users', {term: '@term'});
}])

.factory('BarSearch', ['$resource', function($resource) {
	return $resource('/api/v1/search/bars', {term: '@term'});
}])

.factory('Tab', ['$resource', function($resource) {
	return $resource('/api/v1/tabs/:id');
}])

.factory('Source', ['$resource', function($resource) {
	return $resource('/api/v1/user/sources');
}]);