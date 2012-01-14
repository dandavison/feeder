request = require 'request'
jsdom = require('jsdom')
sys = require 'sys'


class Scraper
    scrape: ->
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
                    _scrape window.jQuery
                )



class DailyCaller extends Scraper
    constructor: ->
        @name = 'dailycaller.com'
        @uri = 'http://dailycaller.com/section/politics/'

    _scrape: ($) ->
        a_elements = $('#widget-most-emailed .category-headline .blue a')

        # .text does not seem to be working with jsdom, so using
        # firstChild.nodeValue instead
        links = (a_elements.map () ->
            text: @firstChild.nodeValue
            url: @href).toArray()

        'most emailed': links


SCRAPER_CLASSES = [DailyCaller]


scrape_all = ->
    data = {}
    for scraper_cls in SCRAPER_CLASSES
        scraper = new scraper_cls
        data[scraper.name] = scraper.scrape()

    sys.puts JSON.stringify(data)


scrape_all()
