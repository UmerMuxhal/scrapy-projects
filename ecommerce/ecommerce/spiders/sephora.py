import json

import scrapy
from scrapy.exceptions import CloseSpider
from urllib.parse import urlencode


class SephoraSpider(scrapy.Spider):
    name = "sephora"
    allowed_domains = ["sephora.com"]
    shops = [
        "makeup-cosmetics",
        "skincare",
        "hair-products",
        "fragrance",
        "makeup-tools",
        "bath-body",
        "travel-size-toiletries",
        "gifts",
    ]
    custom_settings = {
        "FEED_URI": "%(shop)s.csv",
        "FEED_FORMAT": "csv"
    }

    def __init__(self, shop="", **kwargs):
        if shop not in self.shops:
            raise CloseSpider("please enter correct shop value")

        self.start_urls = [
            f'https://www.sephora.com/api/catalog/categories/{shop}/seo?{urlencode(self.get_url_query())}'
        ]
        super().__init__(**kwargs)
        self.shop = shop

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, headers=self.get_headers(), callback=self.parse)

    def parse(self, response):
        result = json.loads(response.text)
        total_products = result.get("totalProducts")
        page_size = result.get("pageSize")
        current_page = result.get("currentPage")
        products = result.get("products")
        for product in products:
            yield {
                "product_id": product["productId"],
                "title": product["displayName"],
                "brand": product["brandName"],
                "price": product["currentSku"]["listPrice"],
                "rating": product["rating"],
                "reviews": product["reviews"],
                "image_url": product["heroImage"],
                "product_url": product["targetUrl"],
            }

        total_pages = int(total_products / page_size)
        if total_products % page_size != 0:
            total_pages = total_pages + 1

        print(f"---------    scraped page: {current_page} / {total_pages}")

        if current_page != total_pages:
            yield response.follow(url=self.construct_new_url(response.url, current_page + 1),
                                  headers=self.get_headers(),
                                  callback=self.parse)

    def construct_new_url(self, url: str, page: int) -> str:
        return url.split("?")[0] + f"?{urlencode(self.get_url_query(current_page=page))}"

    @staticmethod
    def get_url_query(current_page: int = 1, page_size: int = 100) -> dict:
        return {'targetSearchEngine': 'NLP', 'currentPage': f'{current_page}', 'pageSize': f'{page_size}',
                'content': 'true', 'includeRegionsMap': 'true', 'headers': '[object Object]', 'pickupRampup': 'true',
                'sortBy': 'P_NEW:1::P_START_DATE:1', 'sddRampup': 'true', 'loc': 'en-US', 'ch': 'rwd'}

    @staticmethod
    def get_headers():
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.sephora.com/shop/makeup-cosmetics?currentPage=3',
            'EXCLUDE_PERSONALIZED_CONTENT': 'true',
            'x-requested-source': 'rwd',
            'x-timestamp': '1676243584111',
            'x-dtpc': '8$443350495_520h15vRUBMKLLBADGHRKJOFOCIFHAPJMTURJFC-0e0',
            'x-dtreferer': 'https://www.sephora.com/shop/makeup-cosmetics?currentPage=2',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'TE': 'trailers'
        }
