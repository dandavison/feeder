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

    get_link_data: ($aa, text_getter=(a) -> a.href) =>
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
        data['Most popular (need to get article titles)'] = @get_link_data $('#most-popular-category div li a')[0..1]
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

        links = @get_link_data $('.bf-widget div div a')
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


class FoxNews extends Scraper
    constructor: ->
        @name = 'Fox News: Politics'
        @domain = 'http://www.foxnews.com'
        @url = '/politics'

    _scrape: ($, data, callback) =>
        data['Trending in Politics'] = @get_link_data $('.trending-descending li a'), (a) -> a.firstChild.nodeValue
        callback()


class HuffingtonPost extends Scraper
    constructor: ->
        @name = 'Huffington Post'
        @domain = 'http://www.huffingtonpost.com'
        @url = '/news/mostpopular'

    _scrape: ($, data, callback) =>
        links = @get_link_data $('.snp_most_popular a'), (a) -> a.firstChild.nodeValue
        links = (link for link in links when link.text)
        data['Most Popular'] = links
        callback()


class NewYorkTimes extends Scraper
    constructor: ->
        @name = 'New York Times'
        @domain = 'http://www.nytimes.com'
        @url = '/pages/national/'

    _scrape: ($, data, callback) =>
        for [category, name] in [['mostBlogged', 'Most Blogged'], ['mostEmailed', 'Most Emailed'], ['mostViewed', 'Most Viewed']]
            data[name] = @get_link_data $("##{category} li a"), (a) -> a.firstChild.nodeValue
        callback()


class Politico extends Scraper
    constructor: ->
        @name = 'Politico'
        @domain = 'http://www.politico.com'
        @url = '/'

    _scrape: ($, data, callback) =>
        for [category, name] in [['MostRead', 'Most Read'], ['MostEmailed', 'Most Emailed'], ['MostCommented', 'Most Commented']]
            data[name] = @get_link_data $("#popular#{category} ol li a"), (a) -> a.firstChild.nodeValue
        callback()


class WashingtonPost extends Scraper
    constructor: ->
        @name = 'Washington Post: Politics'
        @domain = 'http://www.washingtonpost.com'
        @url = '/politics'

    _scrape: ($, data, callback) =>
        el = $('.most-post ul li span .title')[0]
        # TODO: Should check that [0] corresponds to 'Most Popular',
        # and not 'Top Videos' or 'Top Galleries'
        $aa = $(el).parent().next().find('a')
        data['Most Popular'] = @get_link_data $aa, (a) -> a.firstChild.nodeValue
        callback()


class WSJ extends Scraper
    constructor: ->
        @name = 'WSJ'
        @domain = 'http://online.wsj.com'
        @url = '/public/page/news-world-business.html'

    _scrape: ($, data, callback) =>
        for [category, name] in [['mostRead', 'Most Read'], ['mostEmailed', 'Most Emailed'], ['mostCommented', 'Most Commented']]
            data[name] = @get_link_data $("#mostPopularTab_panel_#{category} ul li a"), (a) -> a.firstChild.nodeValue
        callback()


class WSJWashwire extends Scraper
    constructor: ->
        @name = 'WSJ: washwire'
        @domain = 'http://blogs.wsj.com'
        @url = '/washwire/'

    _scrape: ($, data, callback) =>
        data['All (more work needed to disect them)'] = @get_link_data $('.mostPopular a')
        callback()


SCRAPER_CLASSES = [
    BBCUSandCanada,
#    BuzzFeed,
    DailyCaller,
    FoxNews,
    HuffingtonPost,
    NewYorkTimes,
    Politico,
    WashingtonPost,
    WSJ,
#    WSJWashwire,
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
