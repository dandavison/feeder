request = require 'request'
jsdom = require('jsdom')
sys = require 'sys'

# .text does not seem to be working with jsdom, so using
# firstChild.nodeValue instead


class Scraper
    scrape: (data, callback) ->
        [name, _scrape] = [@name, @_scrape]
        request uri: @uri, (error, response, body) ->
            if error and response.statusCode != 200
                console.error 'Error when contacting #{name}'
                return {}
            jsdom.env(
                {html: body, scripts: ['http://code.jquery.com/jquery-1.5.min.js']},
                (error, window) ->
                    if error
                        console.error 'Error loading jquery'
                        return {}
                    _scrape window.jQuery, data, callback
                )

get_link_data = ($aa, text_getter=(a) -> a.text) ->
    ({text: text_getter(a).trim(), url: a.href} for a in $aa.toArray())



class BuzzFeed extends Scraper
    constructor: ->
        @name = 'buzzfeed'
        @uri = 'http://www.buzzfeed.com/politics'

    _scrape: ($, data, callback) ->
        validate = (url) ->
            (url.indexOf('/usr/homebrew/lib/node/jsdom') == -1) and \
            (url.indexOf('twitter') == -1)

        links = get_link_data $('.bf-widget div div a'), (a) -> a.href
        links = (link for link in links when validate link.url)
        data['Most viral in Politics'] = links
        callback()


class DailyCaller extends Scraper
    constructor: ->
        @name = 'dailycaller'
        @uri = 'http://dailycaller.com/section/politics/'

    _scrape: ($, data, callback) ->
        for category in ['most-emailed', 'most-popular']
            data[category] = get_link_data $("#widget-#{category} .category-headline .blue a"), (a) -> a.firstChild.nodeValue
        callback()


SCRAPER_CLASSES = [
    BuzzFeed,
    DailyCaller,
]


scrape_all = ->
    data = {}
    count = SCRAPER_CLASSES.length
    callback = -> if --count is 0 then sys.puts JSON.stringify(data)

    for scraper_cls in SCRAPER_CLASSES
        scraper = new scraper_cls
        data[scraper.name] = {}
        scraper.scrape(data[scraper.name], callback)


scrape_all()
