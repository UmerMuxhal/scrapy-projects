import scrapy
import scrapy_splash
from scrapy_splash import SplashRequest


class ClutchSpider(scrapy.Spider):
    name = "clutch"
    allowed_domains = ["clutch.co"]
    base_url = "https://clutch.co"
    start_urls = [
        "https://clutch.co/us/agencies/digital-marketing",
        # "https://clutch.co/ca/agencies/digital-marketing",
        # "https://clutch.co/au/agencies/digital-marketing",
        # "https://clutch.co/uk/agencies/digital-marketing",
    ]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy_splash.SplashRequest(url=url,
                                              splash_headers=self.get_headers(),
                                              # endpoint='execute',
                                              args={'wait': 0.5, 'url': "https://clutch.co/us/agencies/digital-marketing"},
                                              callback=self.parse)

    def parse(self, response):
        companies = response.xpath('//div[@class="row"]//h3[@class="company_info"]/text()').extract()
        websites = response.xpath('//div[@class="row"]//a[@class="website-link__item"]/@href').extract()
        services = response.xpath(
            '//div[@class="row"]//div[contains(@class, "directory-graph")]//div[contains(@class, "chart-label")]/span/text()').extract()
        countries = response.xpath(
            '//div[@class="row"]/div[contains(@class, "provider-info")]//span[@class="locality"]/text()').extract()

        # rows = response.xpath('//div[@class="row"]/div[contains(@class, "provider-info")]').extract()

        for company, website, service, country in zip(companies, websites, services, countries):
            yield {
                "Company Name": company,
                "Website Address": website,
                "Service Focus": service,
                "Country": country
            }

        next_page = response.xpath('//li[@class="page-item next"]/a/@href').extarct()
        if next_page is not None:
            next_page = self.base_url + next_page[0]

            yield scrapy_splash.SplashRequest(url=next_page,
                                              headers=self.get_headers(),
                                              # endpoint='render.html',
                                              args={'wait': 0.5},
                                              callback=self.parse)

    def get_headers(self):
        return {
            'authority': 'clutch.co',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'max-age=0',
            'cookie': 'ln_or=eyIyMTU0NjAyIjoiZCJ9; _ga=GA1.1.1273845096.1678629834; _ga_D0WFGX8X3V=GS1.1.1678629833.1.0.1678629833.60.0.0; _gcl_au=1.1.1294122256.1678629834; FPID=FPID2.2.QcIE9wSlIs8%2Fp5hIZ8Fyh%2BdHOxycheKGdryZPtB6W4Y%3D.1678629834; __cf_bm=6A4vmaoGVbg7389VRBHZ9bKUv4.KqUz7HagijxaZqRE-1678629834-0-Abi+Q9jkysNLm+feuFqI/uUxoSrVdv4jjmokXKXhe1WmGL6p6NAEHIxglK31PdirdYH/PWqYhz69iZu0FZf15ZxmgCIuBMGORiwtODHUImaIqW1KnwiD+fnNwFCaxrWVrCRDBDYWBW0eFEPd1SJVgiUow3Kwz6o16cehSPoEiZnA; FPLC=ggcztjom8vl1r3q8R2ojg9bP4OMRqBlBjXz6xbBqHTaaO3k0Ul6Y%2BgkP088FHaifBJ0TrHvi9DQiDOj5xQZ3dNCTQoqbI5OibvFsHe6P9UzZwfk3fnZ9iB43wLhlWg%3D%3D; __hstc=238368351.2413ef3dbcd3280a1813974ab6909d91.1678629836495.1678629836495.1678629836495.1; hubspotutk=2413ef3dbcd3280a1813974ab6909d91; __hssrc=1; __hssc=238368351.1.1678629836497',
            'sec-ch-ua': '"Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
        }
