angular.module('Api', ['ngResource'])

.factory('User', ['$resource', function($resource) {
	return $resource('/api/v1/users/:id');
}])

.factory('Me', ['$resource', function($resource) {
	return $resource('/api/v1/user');
}])

.factory('MePassword', ['$resource', function($resource) {
	return $resource('/api/v1/user/password');
}])

.factory('UserAvatar', ['$resource', function($resource) {
	return $resource('/api/v1/user/avatar', {}, {
    save: {
        method: 'POST',
        // transformRequest: '<THE TRANSFORMATION METHOD DEFINED ABOVE>',
        headers: {'Content-Type': undefined}
    }
  });
}])

.factory('Auth', ['$resource', function($resource) {
	return $resource('/api/v1/auth', {}, {
		logout: {
			method: 'DELETE'
		}
	});
}])

.factory('Search', ['$resource', function($resource) {
	return $resource('/api/v1/search', {term: '@term'});
}])

.factory('UserSearch', ['$resource', function($resource) {
	return $resource('/api/v1/search/users', {term: '@term'});
}]);
