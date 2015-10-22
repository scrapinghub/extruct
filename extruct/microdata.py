"""
Microdata parser

Piece of code extracted form:
* http://blog.scrapinghub.com/2014/06/18/extracting-schema-org-microdata-using-scrapy-selectors-and-xpath/

"""

from scrapy.selector import Selector

def parse_microdata(html):
    selector = Selector(text=html, type='html')
    items = []
    for itemscope in selector.xpath('//*[@itemscope][@itemtype]'):
        item = {"itemtype": itemscope.xpath('@itemtype').extract()[0]}
        item["item_id"] = int(float(itemscope.xpath("""count(preceding::*[@itemscope])
                                                     + count(ancestor::*[@itemscope])
                                                     + 1""").extract()[0]))
        properties = []
        for itemprop in itemscope.xpath("""set:difference(.//*[@itemprop],
                                                          .//*[@itemscope]//*[@itemprop])"""):
            property = {"itemprop": itemprop.xpath('@itemprop').extract()[0]}
            if itemprop.xpath('@itemscope'):
                property["value_ref"] = {
                    "item_id": int(float(itemprop.xpath("""count(preceding::*[@itemscope])
                                                         + count(ancestor::*[@itemscope])
                                                         + 1""").extract()[0]))
                }
            else:
                value = itemprop.xpath('normalize-space(.)').extract()[0]
                if value:
                    property["value"] = value
            attributes = []
            for index, attribute in enumerate(itemprop.xpath('@*'), start=1):
                propname = itemprop.xpath('name(@*[%d])' % index).extract()[0]
                if propname not in ("itemprop", "itemscope"):
                    attributes.append((propname, attribute.extract()))
            if attributes:
                property["attributes"] = dict(attributes)
            properties.append(property)
        item["properties"] = properties
        items.append(item)
    return items

