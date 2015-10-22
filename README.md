Bubba
------------

Custom eBay fashion feed app:
* Parses local Safari bookmarks to obtain link to locally saved eBay searches (urls to searches)
* Parameters of each search are extraced from eBay url links
* The app runs a celery worker to fetch items that match search criteria and performs a set of filters on the items obtained in each search
	* Time filter: removes all items that have been fetched during the last time the app was run 
	* Seller filter: removes items from ignored sellers 
	* Item filter: removes items that have been relisted with the same price
* The items that pass though the filter are displayed by Flask instance in infinite feed fashion (i.e. infinite scroll outline)

