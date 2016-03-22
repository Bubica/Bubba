"""
Instance of this class are used to generate html files that will be added to the feed in infinite scroll script.
"""
import os
class Paginator(object):

    ITEMS_PER_PAGE = 15

    def __init__(self, template_folder):
        
        self.template_folder = template_folder
        self.current_page_cnt = 1
        self.item_buffer = [] #buffers items until there are enough items to be rendered in html page

    def addItems(self, items):

        """ 
        ================================================================================
        Adds items to the interim buffer and creates html pages to be displayed by 
        infinite scroll.

        Dumps the remaining items in a temporary html page (i.e. the ones that remain 
        after filling n pages with ITEMS_PER_PAGE items). This is only done to preserve 
        items in case shutdown signal is received during server operation.
        ================================================================================
        """

        if not items: 
            return
            
        self.item_buffer.extend(items)

        while len(self.item_buffer) >= self.ITEMS_PER_PAGE:

            #Create a new static html
            self.current_page_cnt += 1 #first temp page startes with number 2 - (hardcoded in infinite scroll javascript)
            html_fname = self.template_folder+"/"+"temp"+str(self.current_page_cnt)+".html"

            self._writePg(html_fname, self.item_buffer[:self.ITEMS_PER_PAGE])        
            self.item_buffer = self.item_buffer[self.ITEMS_PER_PAGE:]

        #Write the remaining ones to temp dump file, but keep them in item_buffer as well
        temp_dump_fname = self.template_folder+"/"+"temp_dump.html"
        self._writePg(temp_dump_fname, self.item_buffer)

    def _writePg(self, html_fname, items):

        """
        ================================================================================
        Defines the format of html page. 
        ================================================================================
        """
        f = open(html_fname, 'w')

        f.write("<html>\n") 
        f.write("<body>\n") 
        f.write("<div id=\"container\">")

        #number of items displayed in this page
        for i in range(len(items)):

            entry = items[i]

            f.write("    <div class=\"item default hvr-grow\" data-itemid=\""+str(entry.itemId)+"\" data-searchid=\""+str(entry.searchId)+"\" data-sellerid=\""+str(entry.sellerId)+"\" data-title=\""+str(entry.title)+"\">"+"\n")
            f.write("            <img class=\"tick hidden\" src=\"{{ url_for('static', filename='img/blue-tick.png') }}\">"+"\n")
            f.write("            <h2> " + str(entry.searchName)+ "</h2>"+"\n")
            f.write("            <div class=\"img_wrap\">"+"\n")
            f.write("            <a id=\"itemURL\" href=\""+ str(entry.itemURL) + "\" target=\"_blank\">"+"\n")
            f.write("                   <img src=\""+ str(entry.pictureURL)+"\"/> "+"\n")
            f.write("                   <span class=\"title\"><span>"+str(entry.title)+"</span></span>"+"\n")
            f.write("            </a>"+"\n")
            f.write("            </div>"+"\n")

            if entry.priceCurrency == "USD":
                curr_sign = "&#36;"
            elif entry.priceCurrency == "GBP":
                curr_sign = "&#163;"
            elif entry.priceCurrency == "EUR":
                curr_sign = "&#8364;"
            else:
                curr_sign = ""

            f.write("            <h2> Price: "+curr_sign + " " + str(entry.priceValue) +"</h2>"+"\n")
            f.write("    </div>"+"\n")

        f.write("</div>")
        f.write("</body>\n") 
        f.write("</html>\n")

        f.close()



    def getPgCount(self):
        return self.current_page_cnt



