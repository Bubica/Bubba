
class Result(object):

    """ Bean instance of the result obtained from the server """
    def __init__(self):
        self.title = None
        self.itemId = None
        self.startTime = None
        self.endTime = None
        self.pictureURL = None
        self.itemURL = None
        self.priceValue = None
        self.priceCurrency = None
        self.category = None
        self.sellerId = None
        self.searchName = None
        self.searchId = None

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
        self.priceValue = round(float(value),2)
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

    def __init__(self, id_):
        self.id = id_
        self.d = {}
        self.parentGroup = None
        self.ASPECT_FILTER_TYPES = []

    def setSearchGroup(self, group):
        self.parentGroup = group #pointer to the parent

    def __getitem__(self, key):
        if key in self.d:
            return self.d[key]

        return None

    def __setitem__(self, key, value):
        if value is not None and value != '':
            self.d[key] = value

    def addAspectFilter(self, aspect_filter_type):
        self.ASPECT_FILTER_TYPES.append(aspect_filter_type)

    def getItemFilters(self):
        return filter(lambda x: x in self.ITEM_FILTER_TYPES, self.d.keys())

    def getAspectFilters(self):
        return filter(lambda x: x in self.ASPECT_FILTER_TYPES, self.d.keys())

    def __contains__(self, key):
        return key in self.d.keys()

    #Relying on url alone is fine if I'm using locally parsed bookmarks...
    def __hash__(self):
        # return hash(self.d['url'])
        return hash(self.id)

    def __eq__(self, other):
        if self.__class__ != other.__class__: 
            return False
        return (self.id) == (other.id)

    def __str__(self):
        s = "\n"
        if 'name' in self.d:
            s +="Search name: " + str(self.d['name']) +"\n"

        if 'keywords' in self.d:
            s +="--- keywords: " + str(self.d['keywords']) +"\n"

        if 'categoryId' in self.d:
            s += "--- category: "+ str(self['categoryId'])+ "\n"

        for i in self.getItemFilters():
            s+= "--- item filter: " + i + " = " + str(self[i]) +"\n"

        for i in self.getAspectFilters():
            s+= "--- aspect filter: " + i + " = " + str(self[i]) +"\n"

        return s


