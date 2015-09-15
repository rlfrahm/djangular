angular.module('Api', ['ngResource'])

.factory('User', ['$resource', function($resource) {
	return $resource('/api/v1/users/:id');
}])

.factory('Me', ['$resource', function($resource) {
	return $resource('/api/v1/user');
}])

.factory('Bar', ['$resource', function($resource) {
	return $resource('/api/v1/bars/:id');
}]);