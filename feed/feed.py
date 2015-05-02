import datetime
import dateutil.parser
import pytz

import search
import util.ebay.finding as ebay_find
import util.ebay.trading as ebay_trade
import datetime
from lib import xmltodict


def _update_ended_ignore_items(ignore_list):

    """ 
    Updates all ended items that are placed in user ignore list with relisted item ids.
    Each item on the list is formatted as (search_id, ebay_item_id, ebay_end_time).

    If the ignored item is sold, or has finished and has not been relisted it still stays in the ignore list.
    This is because the seller may decide to relist the item some time in the future and the system should
    attempt to avoid future listings of ignored items as well as the current ones.
    """
    t = datetime.datetime.now(pytz.utc)

    ignore_list_updated = []

    for search_id, id_, end_t in ignore_list:

        print search_id, id_, type(end_t)
        #if the item is still active, leave it in the list
        if end_t > t: 
            ignore_list_updated.append((search_id, id_, end_t))
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
            print "Relisted", list_details['EndTime']
            end_t = dateutil.parser.parse(list_details['EndTime'].strip())
            
        ignore_list_updated.append((search_id, id_, end_t))

    return ignore_list_updated

class UserFeed(object):

    SEARCH_FETCH_TIME = 'lastVisited.log'
    IGNORE_SELLERS_LOG = 'ignoreSellers.log'
    IGNORE_ITEMS_LOG = 'ignoreItemIds.log'

    def __init__(self, userID, log_folder, fetchTDelay = 60):
        # self.categories = {} #matches the name of the category with the id

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
        self.ignored_sellers = []
        for seller in f.readlines(): 
            self.ignored_sellers.append(seller.strip())
        f.close()

        #load ignored items map
        f = open(self.data_folder + self.IGNORE_ITEMS_LOG,'r')
        self.ignored_items = []
        for i in f.readlines():
            search_id, id_, end_t = i.split(',')
            end_t = dateutil.parser.parse(end_t.strip())
            self.ignored_items.append((search_id, id_, end_t))
        f.close()
        self.ignored_items = _update_ended_ignore_items(self.ignored_items)
        

        print "Last log:", self.last_log
        print "Ignored sellers", self.ignored_sellers

    def exit(self):

        """ Dumps all current logs to the user log files """
        
        f = open(self.data_folder + self.IGNORE_SELLERS_LOG, "w")
        for seller_id in self.ignored_sellers:
            f.write(seller_id+"\n")
        f.close()

        f = open(self.data_folder + self.IGNORE_ITEMS_LOG, "w")
        for entry in self.ignored_items:
            f.write(','.join(map(str, entry))+"\n")
        f.close()

        """ Log the fetch time for each search """
        f = open(self.data_folder + self.SEARCH_FETCH_TIME, 'w')
        for s in self.last_log:
            f.write(s +","+str(self.last_log[s])+"\n")
        f.close()

    def addIgnoreSeller(self, seller_id):
        self.ignored_sellers.append(seller_id)

    def addIgnoreItem(self, search_id, item_id):

        item = filter(lambda x: x.itemId==item_id, self.searches[search_id])[0]
        self.ignored_items.append((search_id, item_id, item.endTime))

    def _convert(self, search_name, search_id, res):
        
        """ Converts json object returned from the server into list of search.Result objects"""
        res_ = []
        for item in res:
            item_ = search.Result()
            item_.set_id(item['itemId'][0])
            item_.set_title(item['title'][0])

            #set properties 
            item_.set_startTime(dateutil.parser.parse(item['listingInfo'][0]['startTime'][0]))
            item_.set_endTime(dateutil.parser.parse(item['listingInfo'][0]['endTime'][0]))

            if 'galleryPlusPictureURL' in item: 
                pic_url = item['galleryPlusPictureURL'][0]
            elif 'galleryURL' in item: 
                pic_url = item['galleryURL'][0]

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
            filtered = []
            for item in items:
                print self.last_log[search_id], type(self.last_log[search_id])
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

    def _itemFilter(self, items):
        """
        Filters out all the items that user does not wish to be displayed.
        If such item is relisted, the relisted item will be removed as well.

        TODO: Grossly poor performance. Optimize this!
        """

        filtered = []
        hset = set([i[1] for i in self.ignored_items])
        print
        print hset
        print
        for item in items:
            if item.itemId not in hset:
                filtered.append(item)

        print "Item filter:", len(items), "-->", len(filtered) 
        return filtered

    def loadSearch(self, searchReq):

        """ Obtain search results from ebay for a single search instance """

        #Skip searches that are not spaced enough
        if searchReq.id in self.last_log:
            td = datetime.datetime.now(pytz.utc) - self.last_log[searchReq.id]
            td = td.total_seconds()/60. #in mins
            if td< self.fetchTDelay:
                print "Skipping this search (tdelay threshold)"
                return
    

        prev_fetch_no = None
        prev_filtered_no = None
        pages_total = None

        page_no = 0
        items_total = []
        res_total = []

        #TODO - support all item filters and apply aspect filters as well
        ifilter = []
        for if_name in searchReq.getItemFilters():
            ifilter.append({'name':if_name, 'value':searchReq[if_name]})
        
        afilter = []
        for af_name in searchReq.getAspectFilters():
            afilter.append({'aspectName':af_name, 'aspectValueName':searchReq[af_name]})

        while (not pages_total or page_no < pages_total) and (not prev_fetch_no or prev_fetch_no == prev_filtered_no):

            categoryId = None if 'categoryId' not in searchReq else searchReq['categoryId']
            keywords = None if 'keywords' not in searchReq else searchReq['keywords']

            print categoryId, keywords

            #Perform the search
            res_str = ebay_find.findItemsAdvanced( 
            keywords=keywords, 
            categoryId = categoryId,
            itemFilter = ifilter, 
            aspectFilter = afilter,
            sortOrder = "StartTimeNewest",
            outputSelector = ['SellerInfo', 'PictureURLLarge', 'AspectHistogram'],
            descriptionSearch = searchReq['descriptionSearch'],
            paginationInput = {"entriesPerPage": "100",  "pageNumber" : str(page_no+1)}) #100 items per request seems to be max

            res = eval(res_str)['findItemsAdvancedResponse']
  
            #Read the total number of pages matching this search
            if not pages_total:
                pages_total = int(res[0]['paginationOutput'][0]['totalPages'][0])
                print "Page total no", pages_total, searchReq['url']

            res = res[0]['searchResult'][0]['item']
            page_no +=1
            
            #convert to custom format
            items = self._convert(searchReq['name'], searchReq.id, res)
            prev_fetch_no = len(items) #number of elements fetched from the server

            #Apply filters
            items = self._timeFilter(items, searchReq.id)
            items = self._sellerFilter(items)
            items = self._itemFilter(items)
            prev_filtered_no = len(items) #number of elements retained after time filtering

            items_total.extend(items)

            res_total.extend(res)


        #store all results
        self.searches[searchReq.id] = items_total

        #save the time of search request
        self.last_log[searchReq.id] = datetime.datetime.now(pytz.utc)

        print str(searchReq['name']) + " in " + str(searchReq['categoryId']),
        print " -- Found: %d searches" % (len(res_total),),
        print " -- Filtered: %d" % (len(items_total),),
        print " -- Page cnt: %d"  % (page_no,)

        return items_total


    def get_items(self):

        #Returns all results (accross all searches)
        return [j for i in self.searches.values() for j in i]


