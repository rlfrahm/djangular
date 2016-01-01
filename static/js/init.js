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
