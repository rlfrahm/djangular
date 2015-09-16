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

.factory('Bar', ['$resource', function($resource) {
	return $resource('/api/v1/bars/:id', { id: '@id' });
}])

.factory('Bartenders', ['$resource', function($resource) {
	return $resource('/api/v1/bars/:id/bartenders', { id: '@id' }, {
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
}]);