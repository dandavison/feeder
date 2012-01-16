request = require 'request'
jsdom = require 'jsdom'
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
                        callback()
                    else
                        _scrape window.jQuery, data, callback
                )

    get_link_data: ($aa, text_getter = (a) -> a.firstChild.nodeValue) =>
        url_getter = (a) =>
            if a.href[0] is '/' then @domain + a.href else a.href

        ({text: text_getter(a).trim(), url: url_getter(a)} for a in $aa.toArray())


class TheAtlantic extends Scraper
    constructor: ->
        @name = 'The Atlantic'
        @domain = 'http://www.theatlantic.com'
        @url = '/politics/'

    _scrape: ($, data, callback) =>
        try
            data['Most Popular'] = @get_link_data $('#mostPopular a')
        catch e
            print e
        finally
            callback()


class BBCUSandCanada extends Scraper
    constructor: ->
        @name = 'BBC US & Canada (daily most popular)'
        @domain = 'http://www.bbc.co.uk'
        @url = '/news/world/us_and_canada/'

    _scrape: ($, data, callback) =>
        try
            data['Most popular'] = @get_link_data $('#most-popular-category div li a')[0..1], (a) -> $(a).text()
        catch e
            print e
        finally
            callback()


class BBCUSandCanadaArticle extends Scraper
    constructor: ->
        @name = 'BBC US & Canada'
        @domain = 'http://www.bbc.co.uk'
        @url = '/news/world-us-canada-16549624'

    _scrape: ($, data, callback) =>
        try
            for category in ['Shared', 'Read']
                $aa = $("#most-popular .tab a")
                $aa = $(a for a in $aa.toArray() when $(a).text() is category)
                data[category] = @get_link_data $aa.parent().next().find('li a'), (a) -> $(a).text()
        catch e
            print e
        finally
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

        try
            links = @get_link_data $('.bf-widget div div a'), (a) -> a.href.split('/').pop()
            links = (link for link in links when validate link.url)
            data['Most viral in Politics'] = links
        catch e
            print e
        finally
            callback()


class CNN extends Scraper
    constructor: ->
        @name = 'CNN'
        @domain = 'http://www.cnn.com'
        @url = '/'

    _scrape: ($, data, callback) =>
        try
            data["Popular on Facebook (doesn't work due to facebook auth)"] = @get_link_data $('#pmFacebook li a')
        catch e
            print e
        finally
            callback()


class DailyCaller extends Scraper
    constructor: ->
        @name = 'DailyCaller'
        @domain = 'http://dailycaller.com'
        @url = '/section/politics/'

    _scrape: ($, data, callback) =>
        try
            for [category, name] in [['most-emailed', 'Most emailed'], ['most-popular', 'Most popular']]
                data[name] = @get_link_data $("#widget-#{category} .category-headline .blue a")
        catch e
            print e
        finally
            callback()


class FoxNews extends Scraper
    constructor: ->
        @name = 'Fox News: Politics'
        @domain = 'http://www.foxnews.com'
        @url = '/politics'

    _scrape: ($, data, callback) =>
        try
            data['Trending in Politics'] = @get_link_data $('.trending-descending li a')
        catch e
            print e
        finally
            callback()


class HuffingtonPost extends Scraper
    constructor: ->
        @name = 'Huffington Post'
        @domain = 'http://www.huffingtonpost.com'
        @url = '/'

    _scrape: ($, data, callback) =>
        try
            links = @get_link_data $('.snp_most_popular_entry_desc a'), (a) -> a.href.split('/').pop().split('_n_')[0]
            links = (link for link in links when link.text and link.url.indexOf('javascript') isnt 0)
            data['Most Popular'] = links
        catch e
            print e
        finally
            callback()


class TheNation extends Scraper
    constructor: ->
        @name = 'The Nation'
        @domain = 'http://www.thenation.com'
        @url = '/politics'

    _scrape: ($, data, callback) =>
        try
            for [category, name] in [['most-read', 'Most Read'], ['most-commented', 'Most Commented']]
                data[name] = @get_link_data $("##{category} ul div li a")
        catch e
            print e
        finally
            callback()


class NewYorkTimes extends Scraper
    constructor: ->
        @name = 'New York Times'
        @domain = 'http://www.nytimes.com'
        @url = '/pages/national/'

    _scrape: ($, data, callback) =>
        try
            for [category, name] in [['mostEmailed', 'Most Emailed'], ['mostViewed', 'Most Viewed']]
                data[name] = @get_link_data $("##{category} li a")
        catch e
            print e
        finally
            callback()


class NPR extends Scraper
    constructor: ->
        @name = 'NPR'
        @domain = 'http://www.npr.org'
        @url = '/'

    _scrape: ($, data, callback) =>
        try
            for [category, name] in [['viewed', 'Most Viewed'], ['comm', 'Most Commented (not working?)'], ['mostViewed', 'Most Recommended (not working?)']]
                data[name] = @get_link_data $("#mostpopular .view#{category} ol li a")
        catch e
            print e
        finally
            callback()


class Politico extends Scraper
    constructor: ->
        @name = 'Politico'
        @domain = 'http://www.politico.com'
        @url = '/'

    _scrape: ($, data, callback) =>
        try
            for [category, name] in [['MostRead', 'Most Read'], ['MostEmailed', 'Most Emailed'], ['MostCommented', 'Most Commented']]
                data[name] = @get_link_data $("#popular#{category} ol li a")
        catch e
            print e
        finally
            callback()


class Slate extends Scraper
    constructor: ->
        @name = 'Slate'
        @domain = 'http://www.slate.com'
        @url = '/'

    _scrape: ($, data, callback) =>
        try
            links = @get_link_data $('.most_read_and_commented li a'), (a) -> a.href.split('/').pop()
            links = (link for link in links when link.url isnt 'javascript:void(0)')
            data['Most Read & Most Shared (need to disect them)'] = links
        catch e
            print e
        finally
            callback()


class ThinkProgress extends Scraper
    constructor: ->
        @name = 'ThinkProgress'
        @domain = 'http://thinkprogress.org'
        @url = '/'

    _scrape: ($, data, callback) =>
        try
            data['Facebook & Twitter (need to disect them)'] = @get_link_data $('.popular li a')
        catch e
            print e
        finally
            callback()


class WashingtonExaminer extends Scraper
    constructor: ->
        @name = 'Washington Examiner'
        @domain = 'http://washingtonexaminer.com'
        @url = '/'

    _scrape: ($, data, callback) =>
        try
            data['Most Popular'] = @get_link_data $(".view-popular div ul li a")
        catch e
            print e
        finally
            callback()


class WashingtonPost extends Scraper
    constructor: ->
        @name = 'Washington Post: Politics'
        @domain = 'http://www.washingtonpost.com'
        @url = '/politics'

    _scrape: ($, data, callback) =>
        # FIXME: duplicated method
        try
            $titles = $('.most-post ul li span .title')
            $title = $(title for title in $titles.toArray() when $(title).text() is 'Most Popular')
            $aa = $title.parent().next().find('a')
            data['Most Popular'] = @get_link_data $aa
        catch e
            print e
        finally
            callback()


class WashingtonPostOpinions extends Scraper
    constructor: ->
        @name = 'Washington Post: Opinions'
        @domain = 'http://www.washingtonpost.com'
        @url = '/opinions'

    _scrape: ($, data, callback) =>
        # FIXME: duplicated method
        try
            $titles = $('.most-post ul li span .title')
            $title = $(title for title in $titles.toArray() when $(title).text() is 'Most Popular')
            $aa = $title.parent().next().find('a')
            data['Most Popular'] = @get_link_data $aa
        catch e
            print e
        finally
            callback()


class Wonkette extends Scraper
    constructor: ->
        @name = 'Wonkette'
        @domain = 'http://wonkette.com'
        @url = '/'

    _scrape: ($, data, callback) =>
        try
            for [category, name] in [['most_read_box', 'Most Read'], ['most_commented_box', 'Most Commented']]
                data[name] = @get_link_data $("##{category} ul li a")
        catch e
            print e
        finally
            callback()


class WSJ extends Scraper
    constructor: ->
        @name = 'WSJ'
        @domain = 'http://online.wsj.com'
        @url = '/public/page/news-world-business.html'

    _scrape: ($, data, callback) =>
        try
            for [category, name] in [['mostRead', 'Most Read'], ['mostEmailed', 'Most Emailed'], ['mostCommented', 'Most Commented']]
                data[name] = @get_link_data $("#mostPopularTab_panel_#{category} ul li a")
        catch e
            print e
        finally
            callback()


class WSJWashwire extends Scraper
    constructor: ->
        @name = 'WSJ: washwire'
        @domain = 'http://blogs.wsj.com'
        @url = '/washwire/'

    _scrape: ($, data, callback) =>
        text_getter = (a) ->
            text = a.href
            if text[text.length - 1] == '/'
                text = text.slice(0, text.length - 1)
            text.split('/').pop()
        try
            for category in ['Commented', 'Read']
                # Find the id of the tab with the corresponding title;
                # the links are in a div whose id is determined by the tab id.
                $aa = $(".mostPopular .tab a")
                tab_id = $(a for a in $aa.toArray() when $(a).text() is category).parent().attr("id")
                panel_id = tab_id.replace('_tab_', '_panel_')
                data[category] = @get_link_data $("##{panel_id} li a"), (a) -> $(a).text() or text_getter(a)
        catch e
            print e
        finally
            callback()


class TheWeek extends Scraper
    constructor: ->
        @name = 'The Week'
        @domain = 'http://theweek.com'
        @url = '/'

    _scrape: ($, data, callback) =>
        try
            for [category, name] in [['mostRead', 'Most Read'], ['mostEmailed', 'Most Emailed']]
                # TODO: Why doesn't firstChild.nodeValue work?
                data[name] = @get_link_data $("##{category} a"), (a) -> a.href.split('/').pop()
        catch e
            print e
        finally
            callback()


class Yahoo extends Scraper
    constructor: ->
        @name = 'Yahoo'
        @domain = 'http://news.yahoo.com'
        @url = '/most-popular'

    _scrape: ($, data, callback) =>
        try
            # FIXME: filter condition should be negated
            data['Most popular'] = @get_link_data $(".most-popular-ul li div a").filter("a:has(img)"), (a) -> a.href.split('/').pop()
        catch e
            print e
        finally
            callback()


SCRAPER_CLASSES = [
    TheAtlantic,
    BBCUSandCanadaArticle,
    BBCUSandCanada,
    BuzzFeed, # broken
    CNN, # Popular on Facebook requires facebook access
    DailyCaller,
    FoxNews,
    HuffingtonPost,
    TheNation,
    NewYorkTimes,
    NPR,
    Politico,
    Slate,
    ThinkProgress,
    WashingtonExaminer,
    WashingtonPost,
    WashingtonPostOpinions,
    Wonkette,
    WSJ,
    WSJWashwire, # broken
    TheWeek,
    Yahoo,
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
