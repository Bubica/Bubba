import feed
import search
import setup
from ebay.utils import set_config_file
import pytz
import datetime
import dateutil
import time
from url import ebayBookmarksSafari
import ignore
from collections import defaultdict

# from multiprocessing import Manager
# from multiprocessing import Process

class Launcher(object):

    #TODO: this is cp from UserFeed class
    SEARCH_FETCH_TIME = 'lastVisited.log'
    IGNORE_SELLERS_LOG = 'ignoreSellers.log'
    IGNORE_ITEMS_LOG = 'ignoreItemIds.log'
    IGNORE_ITEMS_HASH_LOG = 'ignoreItemsHash.log'

    eFeed = None
    searchTree = None

    startTime = datetime.datetime.now(pytz.utc)

    def __init__(self, folder = '.'):

        if folder[-1]!='/': folder = folder+'/'
        self.data_folder = folder

        #init ebay module
        setup.init_apikey(self.data_folder)

    def _initUserFeed(self):

        #create feed instance - for each user
        self.eFeed = feed.UserFeed(userID="0", log_folder=self.data_folder, fetchTDelay = 60)

    def _initUserSearches(self):

        #parse local bookmark searches
        self.searchTree, _ = ebayBookmarksSafari.load()
        # self.searchTree = self.searchTree[0][4][0]
        self.lastLoaded = None #points of the search that was previously loaded

    def searchGenerator(self, _last=None):

        """ 
        The result of the search from ebay.
        Returns the generator object to iterate thorugh all searches.

        Walks through the search tree in the inherent order of elements.
        NOTE: The implementation assumes no leaves are of type SearchGroup (i.e. each SearchGroup has at least one child)
        NOTE: if there is more than one instance of the same search in some group, this generator will get stuck in an infinite loop!
        
        next() invocation yields the result of the current search if successful.
        """

        #Initialization
        if not self.eFeed:
            self._initUserFeed()

        if not self.searchTree:
            self._initUserSearches()

        if not _last:
            _last = self.lastLoaded

        elif self.searchTree.index(_last) == len(self.searchTree)-1:
            print "All done"
            raise StopIteration #all searches loaded

        #select the search group
        if not _last:

            #the very beginning
            group = self.searchTree
            i=-1

        else:
            group = _last.parentGroup
            i = group.index(_last)

        if len(group)==0 or i == len(group)-1:
            #level up
            for n in self.searchGenerator(_last = group):
                yield n

        else:
            #there are still unloaded children of this group
            _next = group[i+1]
            
            while _next.__class__ == search.SearchGroup:
                _next = _next[0] #propagate to the first search instance
                
            self.lastLoaded = _next

            #load next search of the same search group, return the result of the search
            g = self.eFeed.loadSearch(_next) #generator accross all pages of ebay search (to speed up seraches returning more than a single page)
            try:
                while True:
                    items = g.next()

                    if items is not None and len(items)>0:
                        self._updateIgnoredItems(self.lastLoaded.id, items)
                    
                    yield items
                
            except StopIteration:
                #All pages of the current search loaded, proceed to the next one
                
                # update fetch time in the db (after the last fetch)
                self._updateFetchTimeLog(self.lastLoaded.id)

                for n in self.searchGenerator():
                    yield n



    def exit(self, ignored_sellers, ignored_items, fetched_searches):

        """ Dump all ignored items and sellers to the user log files """
        self._updateIgnoredSellers(ignored_sellers)

        f = open(self.data_folder + self.IGNORE_ITEMS_LOG, "a")
        for iid in ignored_items:
            f.write(','.join(map(str, iid))+"\n")
        f.close()

    def _updateIgnoredSellers(self, newly_ignored_sellers):

        #copy newly ignored sellers into set structure (to eliminate duplicate entries)
        ignored_sellers = set(newly_ignored_sellers) 

        #load previously ignored sellers
        f = open(self.data_folder + self.IGNORE_SELLERS_LOG, "r")
        ignored_sellers.update([i.strip() for i in list(f.readlines())])
        f.close()

        #store all
        f = open(self.data_folder + self.IGNORE_SELLERS_LOG, "w")
        for sid in ignored_sellers:
            f.write(sid+"\n")
        f.close()

    def _updateIgnoredItems(self, searchid, items):

        """
        Adds new items to ignore items log.
        All irems that have been retrieved will be placed into this log.
        """
        #TODO implement the mechanism for removing ignored items?!
        #TODO better implementation required!
        fname = self.data_folder + self.IGNORE_ITEMS_HASH_LOG

        #load the whole!!! log
        f = open(fname, 'r')
        last_log = defaultdict(set)
        for i in f.readlines():
            s = i.split(',')
            if len(s)<=1: continue
            last_log[s[0]] = set([j.strip() for j in s[1:]]) #each searchid is mapped with the list of ignored items
        f.close()

        #update the items pertaining to this search
        last_log[searchid].update([ignore.ignore_hash(i) for i in items])

        f = open(fname, 'w')
        for s in last_log:
            l = str(s) 
            for i in last_log[s]:
                l += ","+str(i)
            f.write(l + "\n")

        f.close()

    def _updateFetchTimeLog(self, searchid):

        """ Update log time of this search: time of each serach will be set to time app has been started """

        #TODO - this should be the time of fetch and only for displayed searches !

        f = open(self.data_folder + self.SEARCH_FETCH_TIME, 'r')
        last_log = {}
        for i in f.readlines():
            s = i.split(',')
            last_log[s[0]] = dateutil.parser.parse(s[1].strip()) 
        f.close()

        last_log[searchid] = self.startTime #initialize to app start time

        f = open(self.data_folder + self.SEARCH_FETCH_TIME, 'w')
        for s in last_log:
            f.write(s +","+str(last_log[s])+"\n")
        f.close()
