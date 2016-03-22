import hashlib


"""
Handles ignored items
"""
def ignore_hash(item):

    """ Returns the hash of an ignored item """

    m = hashlib.md5()
    m.update(item.searchId)
    m.update(item.title)
    m.update(item.sellerId)
    m.update(str(item.priceValue))

    return m.hexdigest()