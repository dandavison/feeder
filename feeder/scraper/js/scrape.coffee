request = require 'request'
sys = require 'sys'


class DailyCaller
    constructor: ->
        @name = 'dailycaller.com'
        @uri = 'http://dailycaller.com/section/politics/'

    _scrape: (body) ->
        {body}

    scrape: ->
        [name, _scrape] = [@name, @_scrape]
        request uri: @uri, (error, response, body) ->
            if error and response.statusCode != 200
                console.error 'Error when contacting #{name}'
                return {}
            _scrape body


SCRAPER_CLASSES = [DailyCaller]


scrape_all = ->
    data = {}
    for scraper_cls in SCRAPER_CLASSES
        scraper = new scraper_cls
        data[scraper.name] = scraper.scrape()

    sys.puts JSON.stringify(data)


scrape_all()
