request = require 'request'
sys = require 'sys'

request({ uri:'http://www.google.com' }, (error, response, body) ->
    if error and response.statusCode != 200
        console.log('Error when contacting google.com')

    sys.puts(body)
)
