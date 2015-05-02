
class Result(object):

    """ Bean instance of the result obtained from the server """
    def __init__(self):
        self.title = None
        self.itemId = None
        self.searchId = None
        self.startTime = None
        self.endTime = None
        self.pictureURL = None
        self.itemURL = None
        self.priceValue = None
        self.priceCurrency = None
        self.category = None
        self.sellerId = None
        self.searchName = None

    def set_title(self, title):
        self.title = title

    def set_id(self, itemId):
        self.itemId = itemId

    def set_searchId(self, searchId):
        self.searchId = searchId

    def set_startTime(self, sTime):
        self.startTime = sTime
    
    def set_endTime(self, eTime):
        self.endTime = eTime

    def set_pictureURL(self, picURL):
        self.pictureURL = picURL

    def set_price(self, value, currency):
        self.priceValue = value
        self.priceCurrency = currency

    def set_category(self, category):
        self.category = category

    def set_itemURL(self, url):
        self.itemURL = url

    def set_sellerID(self, sellerId):
        self.sellerId = sellerId

    def set_customSearchName(self, searchName):
        self.searchName = searchName
        
    
class SearchGroup(object):
    """ Contains one or more search classes and/or serach instances """
    def __init__(self, name):

        self.name = name
        self.children = []
        self.parentGroup = None

    def addChild(self, child) :
        # print "adding child", self.__str__(), child.__str__()
        self.children.append(child)

    def setParent(self, parentGroup):
        self.parentGroup = parentGroup

    def index(self, child):
        if child in self.children:
            return self.children.index(child)

        return -1

    def __getitem__(self, i):
        return self.children[i]

    def __len__(self):
        return len(self.children)

    def __str__(self):
        s = ""
        if self.parentGroup:
            s += self.parentGroup.__str__()

        s+=" -- "+self.name
        return s

class SearchRequest(object):

    ITEM_FILTER_TYPES = ['ListingType', 'Condition', 'LocatedIn', 'MinPrice', 'MaxPrice', 'MaxDistance', 'ReturnsAcceptedOnly', 'Seller']
    ASPECT_FILTER_TYPES = ['Size', 'Shoe Size', 'Trouser Size', 'Cup Size', 'Chest Size', 'Brand', 'Material', 'Main Colour', 'Color', 'Metal', 'Material', 'Main Stone', 'Style', 'Length']

    def __init__(self, id_):
        self.id = id_
        self.d = {}
        self.parentGroup = None

        #list of paramters that pertain to each filter
        self.itemFilters = []
        self.aspectFilters = []

    def setSearchGroup(self, group):
        self.parentGroup = group #pointer to the parent

    def __getitem__(self, key):
        if key in self.d:
            return self.d[key]

        return None

    def __setitem__(self, key, value):
        if value is not None and value != '':
            self.d[key] = value

    def getItemFilters(self):
        return filter(lambda x: x in self.ITEM_FILTER_TYPES, self.d.keys())

    def getAspectFilters(self):
        return filter(lambda x: x in self.ASPECT_FILTER_TYPES, self.d.keys())

    def __contains__(self, key):
        return key in self.d.keys()

    def __str__(self):
        return str(self['keywords'])+" in "+str(self['categoryId'])


    #Relying on url alone is fine if I'm using locally parsed bookmarks...
    def __hash__(self):
        # return hash(self.d['url'])
        return hash(self.id)

    def __eq__(self, other):
        if self.__class__ != other.__class__: 
            return False
        # return (self.d['url']) == (other.d['url'])
        return (self.id) == (other.id)

    def __str__(self):
        s = ""
        if 'name' in self.d:
            s +="Search: " + str(self.d['name'])

        return s


