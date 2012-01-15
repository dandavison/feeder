request = require 'request'
jsdom = require('jsdom')
sys = require 'sys'

class Scraper
    scrape: (data, callback) ->
        [name, _scrape] = [@name, @_scrape]
        request uri: @domain + @url, (error, response, body) ->
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

    get_link_data: ($aa, text_getter=(a) -> a.text) =>
        # .text does not seem to be working with jsdom, so sometimes using
        # firstChild.nodeValue instead
        url_getter = (a) =>
            if a.href[0] is '/' then @domain + a.href else a.href

        ({text: text_getter(a).trim(), url: url_getter(a)} for a in $aa.toArray())


class BBCUSandCanada extends Scraper
    constructor: ->
        @name = 'BBC US & Canada (daily most popular)'
        @domain = 'http://www.bbc.co.uk'
        @url = '/news/world/us_and_canada/'

    _scrape: ($, data, callback) =>
        data['Most popular'] = @get_link_data $('#most-popular-category div li a')[0..1], (a) -> a.href
        callback()


class BuzzFeed extends Scraper
    constructor: ->
        @name = 'buzzfeed'
        @domain = 'http://www.buzzfeed.com'
        @url = '/politics'

    _scrape: ($, data, callback) =>
        validate = (url) ->
            (url.indexOf('/usr/homebrew/lib/node/jsdom') == -1) and \
            (url.indexOf('twitter') == -1)

        links = @get_link_data $('.bf-widget div div a'), (a) -> a.href
        links = (link for link in links when validate link.url)
        data['Most viral in Politics'] = links
        callback()


class DailyCaller extends Scraper
    constructor: ->
        @name = 'dailycaller'
        @domain = 'http://dailycaller.com'
        @url = '/section/politics/'

    _scrape: ($, data, callback) =>
        for [category, name] in [['most-emailed', 'Most emailed'], ['most-popular', 'Most popular']]
            data[name] = @get_link_data $("#widget-#{category} .category-headline .blue a"), (a) -> a.firstChild.nodeValue
        callback()


SCRAPER_CLASSES = [
    BBCUSandCanada,
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
