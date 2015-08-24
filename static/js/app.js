angular.module('App', ['ui.bootstrap'])

.config(function($interpolateProvider) {
  $interpolateProvider.startSymbol('{[{').endSymbol('}]}');
})

.directive('buyDrinks', [function() {
  return {
    scope: true,
    link: function(scope) {
      scope.order = {
        bar: '',
        bartender: '',
        emails: [],
        drinks: [
          { name: 'Beer', cost: 5 }
        ]
      };
      scope.state = 0;
      scope.setState = function(s) {
        scope.state = s;
      };
      scope.isState = function(s) {
        return (s == scope.state);
      };
      scope.addAnotherEmail = function() {
        console.log(scope.order.emails.length - 1, scope.order.emails, scope.order.emails[scope.order.emails.length - 1]);
        if (scope.order.emails[scope.order.emails.length - 1] != '')
          scope.order.emails.push('');
      };
      scope.setType = function(t) {
        scope.order.type = t;
        if (t == 'me')
          scope.order.emails = [email];
        else
          scope.order.emails = [''];
        scope.setState(1);
      };
    }
  };
}]);