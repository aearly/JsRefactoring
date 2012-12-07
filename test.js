/**
 * This is a mess of a function designed to stress the refactorer and smoke out
 * corner cases
 */
var foo = function (qwer, wert, dovar) {
	var foo = 1 + qwer;

	var asdf = foo + bar(qwer, wert),
		qux = {
			asdf: asdf,
			qwer: 1
		},
		zap = [qwer, wert];

	for (var i = 0; i < asdf; i ++) {
		var q = qwer[i];
	}

	wert(asdf + dovar , function () {
		var a = asdf;
		var b = qwer;
		return function () {
			return foo + a + b;
		};
	});
	// {
	/*
		{
	*/
	var baz = (function () {
		return 0;
	}()),
	sopr;

	return asdf + baz;
};

function sdfg(asdf) {
	return asdf + "asdf";
}
