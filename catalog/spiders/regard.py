import scrapy
import re
import random
from urllib.parse import urljoin
from catalog import items
from scrapy_playwright.page import PageMethod
import json
from inline_requests import inline_requests
from scrapy import Spider, Request

class QuotesSpider(scrapy.Spider):
    count = 1
    res_dict = []
    product_reviews_urls = []
    product_details_urls = []
    product_url_list = []
    product_details = []
    name = 'regard'
    allowed_domains = ['webhook.site', 'regard.ru']
    base_url_regard_ru = "https://www.regard.ru"
    download_delay = random.uniform(0.2, 0.5)
    proxy = {'proxy':'https://168.119.247.195:8888'} #, 'playwright_page_coroutines': {"clickallbtns": PageMethod("evaluate", 'document.querySelectorAll(".CardListingModifications_showMore__D1Wl7").forEach(x=>x.click())'),  }}
#    custom_settings = { "PLAYWRIGHT_LAUNCH_OPTIONS": { "proxy": { "server": "http://92.255.164.166:4145", "username": "", "password": "", }, }  }
#   получаем из списка урлов катогий урлы и отправляем их в метод get_url_to_pages_with_products. 
#    def start_requests(self):

#        with open('category_url_list.json') as json_file:
#            data = json.load(json_file)
#        count = 0
#        for key in data:
#            url = list(key.values())[0]
#            yield scrapy.Request(url, meta=self.proxy, callback=self.get_url_to_pages_with_products)

#            count+=1
#            print(f'{count=} \n {url=} \n')


    def start_requests(self):
#        url = 'https://webhook.site/6787d1fc-1879-4471-9626-c510537e72cd'
        url = 'https://www.regard.ru/catalog/all'

        yield scrapy.Request(url, meta=self.proxy, callback=self.parse)



    def parse(self, response, **kwargs):
        print(f"\n\nSTART def parse \n HELLO\n\n\n in url -- {response.url}\n")
#        print(response.text)
        cookie = response.headers #.getlist('Set-Cookie')
        print(f'{cookie=}')
#  со страницы с каталога получаем категории первого уровня. в res помещаем ссылки на категории 1 уровня
        res = response.css(".CategoryLayout_categoryItem__3IwSp .Categories_wrap__3QSKW .CardCategory_wrap__25KAe::attr(href)").extract()
#  перебираем массив с хрефаcategory_url_list.jsonми и добавляем главный домен в начало строки запроса.
        for url in res: 
            print(f'{url=}')
            joinurl = urljoin(self.base_url_regard_ru, url)
            print(f"{joinurl=}")
            try:
                yield scrapy.Request(joinurl, meta={"proxy": 'https://168.119.247.195:8888'}, callback=self.get_subcategories_2)
            except Exception as e:
                print(f"Exception {e}")
#  получаем на вход страницы по ссылкам с первой страницы категорий
    def get_subcategories_2(self, response, **kwargs):
#        a = input("press enter to continue get_subcategories_2)")
        print(f"\n\n\nSTART def get_subcategories_2\n\n in url -- {response.url}\n")
        print(response.status)
        res = response.css(".Scope_deskTiled__QRhew .Categories_wrap__3QSKW .CardCategory_wrap__25KAe::attr(href)").extract()
        print(f'{res=} type=  {type(res)}')
        res = self.add_domain_to_category_url(res, self.base_url_regard_ru)
        print(f'{res=} type=  {type(res)}')
        count = 0
        try:
            for url in res:
                count+=1
                print(f"for loop count = {count} \n********selfdict************ \n url = {url} \nHELLO")
                self.res_dict.append(url)
                item = items.RegardItem()
                item[f'urls_2_category'] = url
                yield item

        except Exception as e:
            print(f"Exception {e}")

        print('called def save to json')
        for url in res:
            try:
                yield scrapy.Request(url, meta={"proxy": 'https://168.119.247.195:8888'}, callback=self.get_subcategories_3)
            except Exception as e:
                print(f"Exception get_subcategories_2 {e}")
        print("end def get_subcategories_2")


#  получаем на вход страницы по ссылкам со второй страницы категорий
    def get_subcategories_3(self, response, **kwargs):
#        a = input("press enter to continue get_subcategories_3)")
        print(f"START def get_subcategories_3 in url -- {response.url}")
        print(response.status)
        try:
            res = response.css(".Scope_deskTiled__QRhew .Categories_wrap__3QSKW .CardCategory_wrap__25KAe::attr(href)").extract()
            print(f'{res=} type=  {type(res)}')
        except Exception as e:
            print("Not have subcategory. Goto --- def get_url_to_pages_with_products")
            yield scrapy.Request(responce.url, meta={"proxy": 'https://168.119.247.195:8888'}, callback=self.get_url_to_pages_with_products)
        if res:
            print(f'{res=} type=  {type(res)}')
            res = self.add_domain_to_category_url(res, self.base_url_regard_ru)
            print(f'{res=} type=  {type(res)}')
 
            count = 0
            for url in res:
                count+=1
                print(f"for loop count = {count}")
                print(f"url = {url}")
                self.res_dict.append(url)
                item = items.RegardItem()
                item[f'url_to_list_product_category'] = url
                yield item
            for url in res:
                try:
                    yield scrapy.Request(url, meta={"proxy": 'https://168.119.247.195:8888'}, callback=self.get_url_to_pages_with_products)
                except Exception as e:
                    print(f"Exception get_subcategories_2 {e}")
        print("END def get_subcategories_3 in url -- {response.url}")

    def add_domain_to_category_url(self, res, domain):
        res_list = []
        for url in res: 
            print(f'{url=}')
            joinurl = urljoin(self.base_url_regard_ru, url)
            res_list.append(joinurl)
        return res_list










    def get_url_to_pages_with_products(self, response, **kwargs): #  получаем ответ со странице товаров. проверяем, если больше одной пагинации,отправлем на пролистывание, если одна, то отправляем
        list_to_details, list_to_reviews = [], []
        print(f"\nSTART def get_url_to_pages_with_products\n\n in url -- {response.url}\n")
        pages_count = response.css(".Pagination_left__n_bO6 .Pagination_item__link__21lvp::attr(href)").extract()
        print(f'{pages_count=} \n on the page {response.url=}')

        if len(pages_count) > 1:
            pages_count = pages_count[-1]  # количество закладок по одной категории. ДОДЕЛАТЬ
            pages_count = re.search(r"(?<=page=).*", pages_count).group()

            for page in range(int(pages_count)):
               url_to_product_list_page = f'{response.url}?page={page+1}'
               yield scrapy.Request(url_to_product_list_page, meta=self.proxy, callback=self.get_url_to_product_from_one_page)

        else:
            urls_big = response.css(".ListingRenderer_listingCard__XhvNd .Card_row__3FoSA a::attr(href)").extract()
            print(f"\n\n all urls on this page\n{urls_big}\n {len(urls_big)=}")
            all_page_product_urls = urls_big  # убираем повторения в списке урлов
            print(f'{all_page_product_urls=} \n {len(urls_big)=}')

            for url in all_page_product_urls:
                url_to_product = f'{self.base_url_regard_ru}{url}'
                print(f"url to details -- {url_to_product}\n")
                yield scrapy.Request(url_to_product, meta=self.proxy, callback=self.get_details_from_product)

    def get_url_to_product_from_one_page(self, response, **kwargs):
        print(f"\nSTART def get_url_to_product_from_one_page\n\n in url -- {response.url}\n")
        urls_big = response.css(".ListingRenderer_listingCard__XhvNd .Card_row__3FoSA a::attr(href)").extract()
        all_page_product_urls = urls_big  # убираем повторения в списке урлов
        print(f'{all_page_product_urls=} \n {len(urls_big)=}')

        for url in all_page_product_urls:
            url_to_product = f'{self.base_url_regard_ru}{url}'
            print(f"url to details -- {url_to_product}\n")
            yield scrapy.Request(url_to_product, meta=self.proxy, callback=self.get_details_from_product)

    def get_reviews_from_product(self, response, **kwargs):
        print(f"\nSTART def get_reviews_from_product\n\n in url -- {response.url}\n")
#        print(response.text)
#        reviews_grade = response.css('.ProductReviews_wrap__32Tk8').extract() #  #__next > div > div.LayoutWrapper_wrap__Onh8G > main > div > div.Grid_row__ZvFHa.productPage_bottom__2rdYu > div:nth-child(1) > div:nth-child(2) > div:nth-child(3) > div > div.Grid_col__1pxvm.Grid_col-3__3sLo5.Grid_col-tablet-12-12__2aj_r.ProductReviews_rating__2u6YQ > div > div.ReviewRating_total__24PrM > p
#        reviews_grade = response.text # css(".ProductReviews_wrap__32Tk8").get() #  #__next > div > div.LayoutWrapper_wrap__Onh8G > main > div > div.Grid_row__ZvFHa.productPage_bottom__2rdYu > div:nth-child(1) > div:nth-child(2) > div:nth-child(3) > div > div.Grid_col__1pxvm.Grid_col-3__3sLo5.Grid_col-tablet-12-12__2aj_r.ProductReviews_rating__2u6YQ > div > div.ReviewRating_total__24PrM > p
#        text_review = {}
#        text_review["text"] = reviews_grade
#        yield text_review
#        print(f'\n{reviews_grade=}\n')
        return response.status

    @inline_requests
    def get_details_from_product(self, response, **kwargs):
        print(f"\nSTART def get_details_from_product\n\n in url -- {response.url}\n")
        product_reviews_url = response.url + '?tab=reviews'
        product_reviews_page_response = yield Request(product_reviews_url)
        product_reviews_dict = self.get_reviews_from_product(product_reviews_page_response)
        print(f'\n{product_reviews_dict=}\n')
#        yield scrapy.Request(product_revies_url, meta=self.proxy, callback=self.get_reviews_from_product)
        product_details_main = response.css(".CharacteristicsSection_content__dsggI .CharacteristicsItem_item__mn1cf").extract()
        product_details_main_name = self.replace_dots(response.css(".CharacteristicsSection_content__dsggI .CharacteristicsItem_item__mn1cf .CharacteristicsItem_left__gy_I_ .CharacteristicsItem_name__-AhRC span::text").extract())
        product_details_main_value = response.css(".CharacteristicsSection_content__dsggI .CharacteristicsItem_item__mn1cf .CharacteristicsItem_value__3-EWJ .CharacteristicsItem_valueData__3RL19::text").extract()
        product_details_main_href = response.css(".CharacteristicsSection_content__dsggI .CharacteristicsItem_item__mn1cf .CharacteristicsItem_value__3-EWJ .CharacteristicsItem_valueLink__1u3xf").extract()
        product_details_main_producer = response.css(".CharacteristicsSection_content__dsggI .CharacteristicsItem_item__mn1cf .CharacteristicsItem_value__3-EWJ .CharacteristicsItem_valueLink__1u3xf::text").extract()
        product_name = response.css(".Grid_row__ZvFHa .productPage_title__1B1Yw::text").get()
        product_price = response.css(".PriceBlock_bottom__3Dpzh .PriceBlock_priceBlock__VzjwV span::text").get()
        product_price = self.get_price_from_string(product_price)
#        print(f"\n{product_price=}\n")
        product_id = response.css(".ProductMeta_wrap__1BruW").get()
        product_id = re.search(r'<!-- -->(.*?)</p>', product_id).group(1)

        if len(product_details_main_producer) > 1:  #  подготавливаем список описнаие. добавляем в начало списка и в конец производителя и адрес сайта.
            product_details_final_value_list = [product_details_main_producer[0]] + product_details_main_value + [product_details_main_producer[1]]
            product_details_final = dict(zip(product_details_main_name, product_details_final_value_list))

        else:
            product_details_final = dict(zip(product_details_main_name, product_details_main_value))
            product_details_final_value_list = None
            pass

        product_details_final['product_name'] = product_name
        product_details_final['product_price'] = product_price
        product_details_final['product_id'] = product_id
        product_details_final['product_regard_url'] = response.url
        json_product_details_final = {}
        json_product_details_final[product_id] = {'details':product_details_final}
#        json_product_details_final[product_id] = {'reviews':product_reviews_dict}
        yield json_product_details_final
#        print(f'\n\n{product_details_main=} \n\n {product_details_main_name=} \n\n {product_details_main_value=} \n\n {product_details_main_href=} \n\n {product_details_main_producer=} \n\n {product_details_final_value_list}')
#        print(f'\n\n{product_details_final=} \n\n {product_name=} \n\n {product_price=} \n\n {product_id=}')

    def get_price_from_string(self, product_price_str):
        res = ''
        for price_part in product_price_str:
            if price_part.isdigit():
                res = res + price_part
            else:
                continue
        return res

    def replace_dots(self, mas):
        res = []
        for item in mas:
            item = item.replace(".", "")
            if item == "":
                continue
            else:
                res.append(item)
        return res

'''
import scrapy
import re
import random
from urllib.parse import urljoin
from catalog import items

class QuotesSpider(scrapy.Spider):
    count = 1
    res_dict = []
    name = 'regard'
    allowed_domains = ['webhook.site', 'regard.ru']
    base_url_regard_ru = "https://www.regard.ru"
    download_delay = random.uniform(3, 10)
    proxy = {'proxy':'https://168.119.247.195:8888'}
#    custom_settings = { "PLAYWRIGHT_LAUNCH_OPTIONS": { "proxy": { "server": "http://92.255.164.166:4145", "username": "", "password": "", }, }  }
    def start_requests(self):
#        url = 'https://webhook.site/6787d1fc-1879-4471-9626-c510537e72cd'
        url = 'https://www.regard.ru/catalog/all'

        yield scrapy.Request(url, meta=self.proxy, callback=self.parse)



    def parse(self, response, **kwargs):
        print(f"\n\nSTART def parse \n HELLO\n\n\n in url -- {response.url}\n")
#        print(response.text)
        cookie = response.headers #.getlist('Set-Cookie')
        print(f'{cookie=}')
#  со страницы с каталога получаем категории первого уровня. в res помещаем ссылки на категории 1 уровня
        res = response.css(".CategoryLayout_categoryItem__3IwSp .Categories_wrap__3QSKW .CardCategory_wrap__25KAe::attr(href)").extract()
#  перебираем массив с хрефами и добавляем главный домен в начало строки запроса.
        for url in res: 
            print(f'{url=}')
            joinurl = urljoin(self.base_url_regard_ru, url)
            print(f"{joinurl=}")
            try:
                yield scrapy.Request(joinurl, meta={"proxy": 'https://168.119.247.195:8888'}, callback=self.get_subcategories_2)
            except Exception as e:
                print(f"Exception {e}")
#  получаем на вход страницы по ссылкам с первой страницы категорий
    def get_subcategories_2(self, response, **kwargs):
#        a = input("press enter to continue get_subcategories_2)")
        print(f"\n\n\nSTART def get_subcategories_2\n\n in url -- {response.url}\n")
        print(response.status)
        res = response.css(".Scope_deskTiled__QRhew .Categories_wrap__3QSKW .CardCategory_wrap__25KAe::attr(href)").extract()
        print(f'{res=} type=  {type(res)}')
        res = self.add_domain_to_category_url(res, self.base_url_regard_ru)
        print(f'{res=} type=  {type(res)}')
        count = 0
        try:
            for url in res:
                count+=1
                print(f"for loop count = {count} \n********selfdict************ \n url = {url} \nHELLO")
                self.res_dict.append(url)
                item = items.RegardItem()
                item[f'urls_2_category'] = url
                yield item

        except Exception as e:
            print(f"Exception {e}")

        print('called def save to json')
        for url in res:
            try:
                yield scrapy.Request(url, meta={"proxy": 'https://168.119.247.195:8888'}, callback=self.get_subcategories_3)
            except Exception as e:
                print(f"Exception get_subcategories_2 {e}")
        print("end def get_subcategories_2")


#  получаем на вход страницы по ссылкам со второй страницы категорий
    def get_subcategories_3(self, response, **kwargs):
#        a = input("press enter to continue get_subcategories_3)")
        print(f"START def get_subcategories_3 in url -- {response.url}")
        print(response.status)
        try:
            res = response.css(".Scope_deskTiled__QRhew .Categories_wrap__3QSKW .CardCategory_wrap__25KAe::attr(href)").extract()
            print(f'{res=} type=  {type(res)}')
        except Exception as e:
            print("Not have subcategory. Goto --- def get_url_to_pages_with_products")
            yield scrapy.Request(responce.url, meta={"proxy": 'https://168.119.247.195:8888'}, callback=self.get_url_to_pages_with_products)
        if res:
            print(f'{res=} type=  {type(res)}')
            res = self.add_domain_to_category_url(res, self.base_url_regard_ru)
            print(f'{res=} type=  {type(res)}')
 
            count = 0
            for url in res:
                count+=1
                print(f"for loop count = {count}")
                print(f"url = {url}")
                self.res_dict.append(url)
                item = items.RegardItem()
                item[f'url_to_list_product_category'] = url
                yield item
            for url in res:
                try:
                    yield scrapy.Request(url, meta={"proxy": 'https://168.119.247.195:8888'}, callback=self.get_url_to_pages_with_products)
                except Exception as e:
                    print(f"Exception get_subcategories_2 {e}")
        print("END def get_subcategories_3 in url -- {response.url}")

    def add_domain_to_category_url(self, res, domain):
        res_list = []
        for url in res: 
            print(f'{url=}')
            joinurl = urljoin(self.base_url_regard_ru, url)
            res_list.append(joinurl)
        return res_list


    def get_url_to_pages_with_products(self, response, **kwargs):
        print(f"\n\n\n\n!!!!!!!LIST OF PRODUCTS HERE !!!!\n\n\nSTART def get_url_to_pages_with_products for category -- {response.url}")
        print(response.status)
        print(response.url)
        print("START def get_url_to_pages_with_products")

#        a = input("press enter to continue)")

#        res = response.css(".Scope_deskTiled__QRhew .Categories_wrap__3QSKW .CardCategory_wrap__25KAe::attr(href)").extract()
#        print(f'{res=} type=  {type(res)}')



'''













'''


    def save_to_json(self, res, item_name):
        count = 0
        for url in res:
            count+=1
            print(f"for loop count = {count}")
            print(f'{self.res_dict=}')

            print(f"url = {url}")
            print("HELLO")
            self.res_dict.append(url)

            item = items.RegardItem()
            item[f'{item_name}'] = url
        return item

'''

