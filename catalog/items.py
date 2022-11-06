# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
from scrapy.item import Item, Field
import scrapy


class RegardItem(scrapy.Item):
    # define the fields for your item here like:
    text = scrapy.Field()
    author = scrapy.Field()
    tags = scrapy.Field()
    urls_2_category = scrapy.Field()
    urls_3_category = scrapy.Field()
    urls_4_category = scrapy.Field()
    url_to_list_product_category = scrapy.Field()
    url_to_product = scrapy.Field()

    
