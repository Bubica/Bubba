# from ebay.utils import set_config_file
# import shopping_tweaked as shop
# import ebay.shopping as shop

# import ebay.finding as find
# import setup

import feed
import search
import loadEbayBookmarksSafari as bookmarks


def run():
    # categories, last_log = init()

    #load saved searches from local safari browser
    b = bookmarks.load()

    #a single test search - Whistles clothes
    eFeed = feed.SearchFeed()
    for s in b[0][0]:
        req = search.Request()
        req.parseSafariBookmark(s.attrib)
        eFeed.loadSearch(req)



