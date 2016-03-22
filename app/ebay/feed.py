import ignore
import datetime
import dateutil.parser
import pytz
import logging

import setup
import search
import lib_wrapper.finding as ebay_find
import lib_wrapper.trading as ebay_trade
import datetime
from util import xmltodict
from collections import defaultdict

logger = logging.Logger(__file__)

class UserFeed(object):

    #Does not edit logs - only reads the data at the initialization stage
    SEARCH_FETCH_TIME = 'lastVisited.log'
    IGNORE_SELLERS_LOG = 'ignoreSellers.log'
    IGNORE_ITEMS_LOG = 'ignoreItemIds.log'
    IGNORE_ITEMS_HASH_LOG = 'ignoreItemsHash.log'

    def __init__(self, userID, log_folder, fetchTDelay = 60):

        #TODO - something crashing when I invoke this on the server...
        # self.categories.update(setup.loadCategoryIds(root=11450)) # 'Clothes, Shoes & Accessories'
        # self.categories.update(setup.loadCategoryIds(root=281)) # 'Jewellery & Watches'

        self.data_folder = log_folder
        self._loadLogs()

        #store param
        self.fetchTDelay = fetchTDelay #time delay (in mins) between two server fetches

        self.searches = {}

    def _loadLogs(self):
        
        #TODO: make log folder out of user id

        #load time of last log for each search
        f = open(self.data_folder + self.SEARCH_FETCH_TIME, 'r')
        self.last_log = {}
        for i in f.readlines():
            s = i.split(',')
            self.last_log[s[0]] = dateutil.parser.parse(s[1].strip()) 
            #datetime.datetime.strptime(s[1].strip(), "%Y-%m-%d %H:%M:%S")
        f.close()

        #load ignored sellers list
        f = open(self.data_folder + self.IGNORE_SELLERS_LOG,'r')
        self.ignored_sellers = set()
        for seller in f.readlines(): 
            self.ignored_sellers.add(seller.strip())
        f.close()

        #load ignored items map -- TODO remove this
        f = open(self.data_folder + self.IGNORE_ITEMS_LOG,'r')
        self.ignored_items = defaultdict(list)
        for i in f.readlines():
            search_id, id_, end_t = i.split(',')
            end_t = dateutil.parser.parse(end_t.strip())
            self.ignored_items[search_id].append((id_, end_t))
        f.close()

        #load ignored items hashes
        f = open(self.data_folder + self.IGNORE_ITEMS_HASH_LOG,'r')
        self.ignored_items_hash = defaultdict(set)
        for i in f.readlines():
            s = i.split(',')
            if len(s)<=1: continue #TODO: remove this should not have empty lines
            self.ignored_items_hash[s[0]] = set([j.strip() for j in s[1:]]) #each searchid is mapped with the list of ignored items
        f.close()
        

    def _convert(self, search_name, search_id, res):
        
        """ Converts json object returned from the server into list of search.Result objects"""
        res_ = []
        for item in res:
            item_ = search.Result()
            item_.set_id(item['itemId'][0])
            item_.set_title(item['title'][0].replace("\/", "/"))

            #set properties 
            item_.set_startTime(dateutil.parser.parse(item['listingInfo'][0]['startTime'][0]))
            item_.set_endTime(dateutil.parser.parse(item['listingInfo'][0]['endTime'][0]))

            if 'pictureURLLarge' in item: #400 x 400 preferred for feed display
                pic_url = item['pictureURLLarge'][0]
            elif 'pictureURLSuperSize' in item: #800 x 800
                pic_url = item['pictureURLSuperSize'][0]
            elif 'galleryPlusPictureURL' in item: 
                pic_url = item['galleryPlusPictureURL'][0]
            elif 'galleryURL' in item: 
                pic_url = item['galleryURL'][0] #default thumb size
            else:
                continue #some items don't have pics - skip them

            item_.set_pictureURL(pic_url.replace("\/", "/")) #format the url (Mozilla will complain...)
            item_.set_category((item['primaryCategory'][0]['categoryName'], item['primaryCategory'][0]['categoryId']))
            item_.set_price(item['sellingStatus'][0]['currentPrice'][0]['__value__'], item['sellingStatus'][0]['currentPrice'][0]['@currencyId'])
            item_.set_itemURL(item['viewItemURL'][0].translate(None, '\\'))
            item_.set_sellerID(item['sellerInfo'][0]['sellerUserName'][0])
            item_.set_customSearchName(search_name)
            item_.set_searchId(search_id)

            res_.append(item_)

        return res_

    def _timeFilter(self, items, search_id):
        """ 
        Filters out all items listed before self.last_log 
        """

        if search_id not in self.last_log:
            filtered = items
        
        else:
            print "Last log", self.last_log[search_id]
            filtered = []
            for item in items:
                if item.startTime >= self.last_log[search_id]:
                    filtered.append(item)


        print "Time filter:", len(items), "-->", len(filtered)
        return filtered

    def _sellerFilter(self, items):
        """ 
        Filters out all items that are listed by sellers on the ignore list 
        """
        filtered = []
        for item in items:
            if item.sellerId not in self.ignored_sellers:
                filtered.append(item)

        print "Seller filter:", len(items), "-->", len(filtered)  
        return filtered

    def _itemFilter(self, search_id, items):
        """
        Filters out all the items that user does not wish to be displayed.
        Items are compared using their hash values.
        If such item is relisted, the relisted item will be removed as well
        (as long hashes of the original item and relisted item match).
        """

        filtered = []
        hset = self.ignored_items_hash[search_id]
        print "Item filter : size " + str(len(hset))
        for item in items:
            item_hash = ignore.ignore_hash(item)
            if item_hash not in hset:
                filtered.append(item)

        print "Item filter:", len(items), "-->", len(filtered) 
        return filtered

    def loadSearch(self, searchReq):

        """ Obtain search results from ebay for a single search instance """

        #Skip searches that are not spaced enough
        # TODO: move this into feed_launcher
        # if searchReq.id in self.last_log:
        #     td = datetime.datetime.now(pytz.utc) - self.last_log[searchReq.id]
        #     td = td.total_seconds()/60. #in mins
        #     if td< self.fetchTDelay:
        #         print "Skipping this search (tdelay threshold)"
        #         return
    
        #Update ignore items from this search
        # self._update_ignore_items(searchReq.id) #TODO: do this in a scheduled manner while browsing is not in progress

        #init ebay module - TODO this is done for each search separately  since they may refer to different ebay domains (do this more elegantly)
        setup.init_site(self.data_folder, siteid = searchReq['domain'])

        prev_fetch_no = None
        prev_time_filtered_no = None
        pages_total = None

        page_no = 0
        self.searches[searchReq.id] = []
        res_total = []

        #TODO - support all item filters and apply aspect filters as well
        ifilter = []
        for if_name in searchReq.getItemFilters():
            ifilter.append({'name':if_name, 'value':searchReq[if_name]})
        
        afilter = []
        for af_name in searchReq.getAspectFilters():
            afilter.append({'aspectName':af_name, 'aspectValueName':searchReq[af_name]})

        while (not pages_total or page_no < pages_total) and (not prev_fetch_no or prev_fetch_no == prev_time_filtered_no):

            categoryId = None if 'categoryId' not in searchReq else searchReq['categoryId']
            keywords = None if 'keywords' not in searchReq else searchReq['keywords']

            #Perform the search
            res_str = ebay_find.findItemsAdvanced( 
            keywords=keywords, 
            categoryId = categoryId,
            itemFilter = ifilter, 
            aspectFilter = afilter,
            sortOrder = "StartTimeNewest",
            outputSelector = ['SellerInfo', 'PictureURLLarge', 'PictureURLSuperSize', 'AspectHistogram'],
            descriptionSearch = searchReq['descriptionSearch'],
            paginationInput = {"entriesPerPage": "100",  "pageNumber" : str(page_no+1)}) #100 items per request seems to be max

            res = eval(res_str)['findItemsAdvancedResponse']
  
            #some weird error?!
            if 'paginationOutput' not in res[0]:
                print "ERR"
                logger.error("No paginationOutput")
                print res[0]
                return

            #Read the total number of pages matching this search
            if pages_total is None:
                #init total number of pages
                pages_total = int(res[0]['paginationOutput'][0]['totalPages'][0])
                print "Page total no", pages_total, searchReq['url']
            
            if pages_total == 0:
                #No results of this search found
                print "No results", searchReq
                print res[0]['paginationOutput'][0]
                break

            res = res[0]['searchResult'][0]['item']

            page_no +=1
            
            #convert to custom format
            items = self._convert(searchReq['name'], searchReq.id, res)
            prev_fetch_no = len(items) #number of elements fetched from the server

            #Apply filters
            items = self._timeFilter(items, searchReq.id)
            prev_time_filtered_no = len(items) #number of elements retained after time filtering
            # items = self._sellerFilter(items)
            # items = self._itemFilter(searchReq.id, items)

            if len(items)>0:
                self.searches[searchReq.id].extend(items) #store items of this page
                yield items

                # res_total.extend(res)

        #update the fetch time of search request
        self.last_log[searchReq.id] = datetime.datetime.now(pytz.utc)


    def get_items(self):

        #Returns all results (accross all searches)
        return [j for i in self.searches.values() for j in i]


    def _update_ignore_items(self, search_id):

        """ 
        Updates all ended items that are placed in user ignore list with relisted item ids.
        Each item on the list is formatted as (search_id, ebay_item_id, ebay_end_time).

        If the ignored item is sold, or has finished and has not been relisted it still stays in the ignore list.
        This is because the seller may decide to relist the item some time in the future and the system should
        attempt to avoid future listings of ignored items as well as the current ones.

        TODO: checking if the item has been relisted should be done while the feed fetch is not in progress (scheduled time on server...)
        """
        t = datetime.datetime.now(pytz.utc)

        ignore_list_prev = self.ignored_items[search_id]
        ignore_list_updated = []

        for id_, end_t in ignore_list_prev:

            #if the item is still active, leave it in the list
            if end_t > t: 
                ignore_list_updated.append( (id_, end_t))
                continue 

            #item has ended, fetch the status from the server
            status = xmltodict.parse(ebay_trade.GetItem(id_))

            #check if it has been relisted first (since it might have been sold and relisted)
            list_details = status['GetItemResponse']['Item']['ListingDetails']

            while 'RelistedItemID' in list_details: 

                #substitute the old item with relisted one
                id_ = str(list_details['RelistedItemID'])

                #repeat the process for the new item (which might have also finished)
                status = xmltodict.parse(ebay_trade.GetItem(id_))
                list_details = status['GetItemResponse']['Item']['ListingDetails']
                end_t = dateutil.parser.parse(list_details['EndTime'].strip())
                
            ignore_list_updated.append((id_, end_t))

        self.ignored_items[search_id] = ignore_list_updated