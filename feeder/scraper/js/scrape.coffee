request = require 'request'
jsdom = require('jsdom')
sys = require 'sys'


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



class DailyCaller extends Scraper
    constructor: ->
        @name = 'dailycaller.com'
        @uri = 'http://dailycaller.com/section/politics/'

    _scrape: ($, data, callback) ->
        a_elements = $('#widget-most-emailed .category-headline .blue a')
        # .text does not seem to be working with jsdom, so using
        # firstChild.nodeValue instead
        links = (a_elements.map () ->
            text: @firstChild.nodeValue
            url: @href).toArray()
        data['most emailed'] = links
        callback()


SCRAPER_CLASSES = [DailyCaller]


scrape_all = ->
    data = {}
    count = SCRAPER_CLASSES.length
    callback = -> if --count is 0 then sys.puts JSON.stringify(data)

    for scraper_cls in SCRAPER_CLASSES
        scraper = new scraper_cls
        data[scraper.name] = {}
        scraper.scrape(data[scraper.name], callback)


scrape_all()
