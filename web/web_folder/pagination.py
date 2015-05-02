"""
Instance of this class are used to generate html files that will be added to the feed in infinite scroll script.
"""
import os
class Paginator(object):

    ITEMS_PER_PAGE=10

    def __init__(self, template_folder):
        
        self.template_folder = template_folder
        self.current_page_cnt = 1
        self.item_buffer = [] #buffers items until there are enough items to be rendered in html page

    def addItems(self, items):

        """ Adds items to the interim buffer and creates temp html pages to be displayed by infinite scroll """

        if not items: 
            return
            
        self.item_buffer.extend(items)

        while len(self.item_buffer)>=self.ITEMS_PER_PAGE:

            #Create a new static html
            self.current_page_cnt += 1 #first temp page startes with number 2 - (hardcoded in infinite scroll javascript)

            html_fname = self.template_folder+"/"+"temp"+str(self.current_page_cnt)+".html"
            f = open(html_fname, 'w')

            f.write("<html>\n") 
            f.write("<body>\n") 
            f.write("<div id=\"container\">")

            for i in range(self.ITEMS_PER_PAGE):
                entry = self.item_buffer[i]

                f.write("    <div class=\"item default hvr-grow\" data-itemid=\""+str(entry.itemId)+"\" data-searchid=\""+str(entry.searchId)+"\" data-sellerid=\""+str(entry.sellerId)+"\">"+"\n")
                f.write("            <img class=\"tick hidden\" src=\"{{ url_for('static', filename='img/blue-tick.png') }}\">"+"\n")
                f.write("            <h2> " + str(entry.searchName)+ "</h2>"+"\n")
                f.write("            <a id=\"itemURL\" href=\""+ str(entry.itemURL) + "\" target=\"_blank\">"+"\n")
                f.write("                   <img src=\""+ str(entry.pictureURL)+"\"/> "+"\n")
                f.write("            </a>"+"\n")
                if entry.priceCurrency =="USD":
                    curr_sign = "&#36;"
                elif entry.priceCurrency =="GBP":
                    curr_sign = "&#163;"
                else:
                    curr_sign = ""

                f.write("            <h2> Price: "+curr_sign + " " + str(entry.priceValue) +"</h2>"+"\n")
                # f.write("            <a href=\"" + str(entry.itemURL) +"\" class=\"button hvr-grow hidden\" target=\"_blank\">View</a>")
                # f.write("            <a href=\"#\" class=\"button hvr-grow hidden\" id = \"ignore_seller\" name=\""+ str(entry.sellerId)+"\">Ignore this seller</a>")
                # f.write("        </span>"+"\n")
                f.write("    </div>"+"\n")

            f.write("<\div>")
            f.write("</body>\n") 
            f.write("</html>\n")

            f.close()
            self.item_buffer = self.item_buffer[self.ITEMS_PER_PAGE:]


    def getPgCount(self):
        return self.current_page_cnt



