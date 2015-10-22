import ebay.shopping as shop
from ebay.utils import set_config_file
import csv
import os.path

#Setup - put in __init__.py

true = True
false = False

CATEGORIES_FILE="categories.csv"
API_KEY_FILE = None
EBAY_SITE_FILE = None

def init_apikey(folder="./"):
    if folder[-1]!='/': folder += '/'

    global API_KEY_FILE
    API_KEY_FILE = folder + "ebay.apikey"

def init_site(folder="./", siteid = "UK"):
    
    if folder[-1]!='/': folder += '/'

    global API_KEY_FILE
    global EBAY_SITE_FILE
    
    EBAY_SITE_FILE = folder + "ebay.site" + siteid
    set_config_file([API_KEY_FILE, EBAY_SITE_FILE])

def loadCategoryIds(root=-1):

    if os.path.isfile(CATEGORIES_FILE):
        
        #load categories file
        reader = csv.reader(open(CATEGORIES_FILE, 'r'), delimiter='|')

        categories_file = {}
        categories = {} #contains only the requested category and its subcategories
        cat_prefix = None

        for row in reader:
            id_ = int(row[1])
            if id_ == root:
                cat_prefix = row[0]
            categories_file[row[0]] =  id_

        if cat_prefix: 
            #category and its subcategories contained in the file
            for c in categories_file:
                if cat_prefix in c:
                    categories[c] = categories_file[c]

            return categories

    #No file or no requested category in the file - load it 
    categories = {}
    _loadCategoryIds(categories, root)

    #DUMP TO CSV FILE
    f = open(CATEGORIES_FILE, "a")
    writer = csv.writer(f, delimiter='|')
    for cat in categories:
        writer.writerow([cat, categories[cat]])

    f.flush()
    f.close()

    return categories

def _loadCategoryIds(categories_total, root=-1):

    print "ROOT", root

    cat_ = eval(shop.GetCategoryInfo(encoding='JSON', category_id=root, include_selector='ChildCategories')) #root category == -1
    categories = {}
    for c in cat_['CategoryArray']['Category']:

        if c['CategoryID'] == '-1' : 
            name = 'Root'
            id_ = -1
        else:
            name = c['CategoryNamePath']
            id_ = int(c['CategoryID'])
        
        print c['CategoryID'], type(c['CategoryID'])

        categories[name] = id_

    #Recurse to children
    for sub_cat in categories:
        if categories[sub_cat] == root: 
            continue

        _loadCategoryIds(categories_total, root=categories[sub_cat])

    categories_total.update(categories)

