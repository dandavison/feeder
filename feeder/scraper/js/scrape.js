(function() {
  var request, sys;
  request = require('request');
  sys = require('sys');
  request({
    uri: 'http://www.google.com'
  }, function(error, response, body) {
    if (error && response.statusCode !== 200) {
      console.log('Error when contacting google.com');
    }
    return sys.puts(body);
  });
}).call(this);
