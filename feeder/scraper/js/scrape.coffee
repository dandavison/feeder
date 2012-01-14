request = require 'request'
sys = require 'sys'


scrape_daily_caller = ->
    request uri: 'http://dailycaller.com/section/politics/', (error, response, body) ->
        if error and response.statusCode != 200
            console.error 'Error when contacting dailycaller'
            return {}

        {body}


SCRAPERS =
    dailycaller: scrape_daily_caller


scrape_all = ->
    data = {}
    for name of SCRAPERS
        data[name] = SCRAPERS[name]()

    sys.puts JSON.stringify(data)


scrape_all()
