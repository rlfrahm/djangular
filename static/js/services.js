angular.module('App')

.service('Time', [function() {
	this.secM = 60;
	this.secH = 3600;
	this.secD = 86400;

	this.diff = function(t1, t2) {
		var diff = t1.getTime() - t2.getTime();
		return format(Math.abs(diff / 1000));
	};

	function format(input) {
		if (input < 1) return '1 second';
		else if (input < 60) return input + ' seconds';
		else if (input < 3600) return Math.round(input / 60) + ' minutes';
		else if (input < 86400) return Math.round(input / 3600) + ' hours';
		else return Math.round(input / 86400) + ' days';
	}

	this.diff.prototype.format = function() {
		if (this < 60) return this + ' seconds';
		else if (this < 3600) return Math.round(this / 60) + ' minutes';
		else if (this < 86400) return Math.round(this / 3600) + ' hours';
		else return Math.round(this / 86400) + ' days';
	};
}])

.service('Analytics', function() {
	this.pageview = function(title) {
		if (title)
			document.title = title + ' - ';
		document.title += 'My Drink Nation';
		ga('send', 'pageview');
	};

	this.event = function(c, a, l ,v) {
		ga('send', 'event', c, a, l, v);
	};
});