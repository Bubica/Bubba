import feed
import search
import setup
from ebay.utils import set_config_file
import datetime
import time
from url import ebayBookmarksSafari

from multiprocessing import Manager
from multiprocessing import Process

class Launcher(object):

    # visitLog = 'lastVisited.log'
    # ignoreSellersLog = 'ignoreSellers.log'
    # ignoreItemsLog = 'ignoreItemIds.log'

    def __init__(self, folder = '.'):

        if folder[-1]!='/': folder = folder+'/'
        self.data_folder = folder

        #init ebay module
        print "SETUP"
        setup.init(self.data_folder)

        #create feed instance - for each user
        self.eFeed = feed.UserFeed(userID="0", log_folder=self.data_folder, fetchTDelay = 60)

        #parse local bookmark searches
        self.searchTree, self.searchCnt = ebayBookmarksSafari.load()
        self.lastLoaded = None #points ot the search that was previously loaded

        #create manager for parallel access
        # self.accessManager = Manager()

    def log_feed_launch(self):
        """
        Logs current time as the last feed launch
        """
        self.eFeed.exit()
      

    def log_ignored_seller(self, seller_id):
        self.eFeed.addIgnoreSeller(seller_id)



    # """ Obtain searches from ebay"""
    # def loadAll(self):

    #     # #load saved searches from local safari browser
    #     # if not root:
    #     #     root, cnt = ebayBookmarksSa.load()
    #     #     root = root.children[0] #UK only

    #     #a single folder test search (daily searches only)
    #     for s in root.children[:3]:

    #         if s.__class__ == search.SearchGroup:
    #             print s.name
    #             self.load_from_bookmarks(s)

    #         else:
    #             #load the search and store the result in feed instance
    #             self.eFeed.loadSearch(s)

    #     return self.eFeed.get_items()


    def runNext(self, _last=None):

        """ 
        The result of the search from ebay
        Walks through the search tree in the inherent order of elements.
        NOTE: The implementation assumes no leaves are of type SearchGroup (i.e. each SearchGroup has at least one child)

        Returns the result of the search if successful, or None if all searches have been performed.
        """

        #TODO  - remove debug only
        if len(self.eFeed.searches)>=10:
            return None 

        if not _last:
            _last = self.lastLoaded

        elif self.searchTree.index(_last) == len(self.searchTree)-1:
            return None #all searches loaded

        #select the search group
        if not _last:
            #very beginning
            group = self.searchTree
            i=-1

        else:
            group = _last.parentGroup
            i = group.index(_last)

        if len(group)==0 or i == len(group)-1:
            return self.loadNext(_last = group) #level up

        else:
            #there are still unloaded children of this group
            _next = group[i+1]
            
            while _next.__class__ == search.SearchGroup:
                _next = _next[0] #propagate to the first search instance
                
            self.lastLoaded = _next
            return self.eFeed.loadSearch(_next) #load next element of the same group, return the result of the search

        # return self.eFeed.searches[_next.id] #return the result of this search
