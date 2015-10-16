angular.module('App')

.factory('buildAddress', [function() {
  return function(d) {
    return d.street + ', ' + d.city + ', ' + d.province + ' ' + d.postal;
  };
}])
