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

    get_link_data: ($aa, text_getter = (a) -> a.firstChild.nodeValue) =>
        # .text does not seem to be working with jsdom, so sometimes using
        # firstChild.nodeValue instead
        url_getter = (a) =>
            if a.href[0] is '/' then @domain + a.href else a.href

        ({text: text_getter(a).trim(), url: url_getter(a)} for a in $aa.toArray())


class TheAtlantic extends Scraper
    constructor: ->
        @name = 'The Atlantic'
        @domain = 'http://www.theatlantic.com'
        @url = '/politics/'

    _scrape: ($, data, callback) =>
        data['Most Popular'] = @get_link_data $('#mostPopular a')
        callback()


class BBCUSandCanada extends Scraper
    constructor: ->
        @name = 'BBC US & Canada (daily most popular)'
        @domain = 'http://www.bbc.co.uk'
        @url = '/news/world/us_and_canada/'

    _scrape: ($, data, callback) =>
        data['Most popular (need to get article titles)'] = @get_link_data $('#most-popular-category div li a')[0..1], (a) -> a.href.split('/').pop()
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

        links = @get_link_data $('.bf-widget div div a'), (a) -> a.href.split('/').pop()
        links = (link for link in links when validate link.url)
        data['Most viral in Politics'] = links
        callback()


class CNN extends Scraper
    constructor: ->
        @name = 'CNN'
        @domain = 'http://www.cnn.com'
        @url = '/'

    _scrape: ($, data, callback) =>
        data['Popular on Facebook'] = @get_link_data $('#pmFacebook li a')
        callback()


class DailyCaller extends Scraper
    constructor: ->
        @name = 'DailyCaller'
        @domain = 'http://dailycaller.com'
        @url = '/section/politics/'

    _scrape: ($, data, callback) =>
        for [category, name] in [['most-emailed', 'Most emailed'], ['most-popular', 'Most popular']]
            data[name] = @get_link_data $("#widget-#{category} .category-headline .blue a")
        callback()


class FoxNews extends Scraper
    constructor: ->
        @name = 'Fox News: Politics'
        @domain = 'http://www.foxnews.com'
        @url = '/politics'

    _scrape: ($, data, callback) =>
        data['Trending in Politics'] = @get_link_data $('.trending-descending li a')
        callback()


class HuffingtonPost extends Scraper
    constructor: ->
        @name = 'Huffington Post'
        @domain = 'http://www.huffingtonpost.com'
        @url = '/'

    _scrape: ($, data, callback) =>
        links = @get_link_data $('.snp_most_popular_entry_desc a'), (a) -> a.href.split('/').pop()
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
            data[name] = @get_link_data $("##{category} li a")
        callback()


class NPR extends Scraper
    constructor: ->
        @name = 'NPR'
        @domain = 'http://www.npr.org'
        @url = '/'

    _scrape: ($, data, callback) =>
        for [category, name] in [['viewed', 'Most Viewed'], ['comm', 'Most Commented (not working?)'], ['mostViewed', 'Most Recommended (not working?)']]
            data[name] = @get_link_data $("#mostpopular .view#{category} ol li a")
        callback()


class Politico extends Scraper
    constructor: ->
        @name = 'Politico'
        @domain = 'http://www.politico.com'
        @url = '/'

    _scrape: ($, data, callback) =>
        for [category, name] in [['MostRead', 'Most Read'], ['MostEmailed', 'Most Emailed'], ['MostCommented', 'Most Commented']]
            data[name] = @get_link_data $("#popular#{category} ol li a")
        callback()


class Slate extends Scraper
    constructor: ->
        @name = 'Slate'
        @domain = 'http://www.slate.com'
        @url = '/'

    _scrape: ($, data, callback) =>
        links = @get_link_data $('.most_read_and_commented li a'), (a) -> a.href.split('/').pop()
        links = (link for link in links when link.url isnt 'javascript:void(0)')
        data['Most Read & Most Shared (need to disect them)'] = links
        callback()


class ThinkProgress extends Scraper
    constructor: ->
        @name = 'ThinkProgress'
        @domain = 'http://thinkprogress.org'
        @url = '/'

    _scrape: ($, data, callback) =>
        data['Facebook & Twitter (need to disect them)'] = @get_link_data $('.popular li a')
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
        data['Most Popular'] = @get_link_data $aa
        callback()


class WSJ extends Scraper
    constructor: ->
        @name = 'WSJ'
        @domain = 'http://online.wsj.com'
        @url = '/public/page/news-world-business.html'

    _scrape: ($, data, callback) =>
        for [category, name] in [['mostRead', 'Most Read'], ['mostEmailed', 'Most Emailed'], ['mostCommented', 'Most Commented']]
            data[name] = @get_link_data $("#mostPopularTab_panel_#{category} ul li a")
        callback()


class WSJWashwire extends Scraper
    constructor: ->
        @name = 'WSJ: washwire'
        @domain = 'http://blogs.wsj.com'
        @url = '/washwire/'

    _scrape: ($, data, callback) =>
        data['All (more work needed to disect them)'] = @get_link_data $('.mostPopular a'), (a) -> a.href.split('/').pop()
        callback()


class TheWeek extends Scraper
    constructor: ->
        @name = 'The Week'
        @domain = 'http://theweek.com'
        @url = '/'

    _scrape: ($, data, callback) =>
        for [category, name] in [['mostRead', 'Most Read'], ['mostEmailed', 'Most Emailed']]
            # TODO: Why doesn't firstChild.nodeValue work?
            data[name] = @get_link_data $("##{category} a"), (a) -> a.href.split('/').pop()
        callback()


SCRAPER_CLASSES = [
    TheAtlantic,
    BBCUSandCanada,
#    BuzzFeed, # broken
#    CNN, # Popular on Facebook requires facebook access
    DailyCaller,
    FoxNews,
    HuffingtonPost,
    NewYorkTimes,
    NPR,
    Politico,
    Slate,
    ThinkProgress,
    WashingtonPost,
    WSJ,
#    WSJWashwire, # broken
    TheWeek,
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
