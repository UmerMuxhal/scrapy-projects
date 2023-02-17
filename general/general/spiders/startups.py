import json
import scrapy
from urllib.parse import urlencode


class StartupsSpider(scrapy.Spider):
    name = "startups"
    allowed_domains = ["ycombinator.com", "algolianet.com"]

    def __init__(self, **kwargs):
        self.start_urls = [
            f'https://45bwzj1sgc-1.algolianet.com/1/indexes/*/queries?{urlencode(self.get_url_query())}'
        ]
        super().__init__(**kwargs)

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(method="POST", url=url,
                                 headers=self.get_headers(),
                                 body=self.get_request_body(),
                                 callback=self.parse)

    def parse(self, response):
        result = json.loads(response.text).get("results")
        hits = result[0]["hits"]
        for hit in hits:
            yield {
                "Title": hit.get("title"),
                "Tagline": hit.get("tagline"),
                "Created at": hit.get("created_at"),
                "Company Name": hit["company"].get("name"),
                "Company URL": hit["company"].get("url"),
                "Company Logo": hit["company"].get("logo"),
                "Industry": hit["company"].get("industry"),
                "User Name": hit["user"].get("name"),
                "User Avatar": hit["user"].get("avatar"),
                "Total Votes": hit.get("total_vote_count"),
                "Tags": ", ".join(hit["company"].get("tags")),
            }

        total_pages = int(result[0]["nbPages"])
        next_page = int(result[0]["page"]) + 1
        if total_pages != next_page:
            yield scrapy.Request(method="POST", url=self.start_urls[0],
                                 headers=self.get_headers(),
                                 body=self.get_request_body(current_page=next_page),
                                 callback=self.parse)

    @staticmethod
    def get_url_query() -> dict:
        return {
            'x-algolia-agent': 'Algolia^%^20for^%^20JavaScript^%^20(4.11.0)^%^3B^%^20Browser^%^20(lite)',
            'x-algolia-api-key': 'YjVhMWQ1OGEwZTBkNzc3MTk0NzJjODFjMDNjOTM3ODlmZGY0ODdmZTc2OGY3NGY0NGU3ZGIwYTk0ZDJlYWYyZHJlc3RyaWN0SW5kaWNlcz0lNUIlMjJMYXVuY2hlc19wcm9kdWN0aW9uJTIyJTJDJTIyTGF1bmNoZXNfYnlfZGF0ZV9wcm9kdWN0aW9uJTIyJTVEJnRhZ0ZpbHRlcnM9JTVCJTIyeWNkY19wdWJsaWMlMjIlNUQmYW5hbHl0aWNzVGFncz0lNUIlMjJ5Y2RjJTIyJTVE',
            'x-algolia-application-id': '45BWZJ1SGC'
        }

    @staticmethod
    def get_headers() -> dict:
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.ycombinator.com/',
            'content-type': 'application/x-www-form-urlencoded',
            'Origin': 'https://www.ycombinator.com',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
        }

    @staticmethod
    def get_request_body(current_page: int = 1, hits_per_page: int = 30) -> str:
        return json.dumps({
            "requests": [
                {
                    "indexName": "Launches_by_date_production",
                    "query": "",
                    "page": current_page,
                    "facets": [
                        "company.batch",
                        "company.industry"
                    ],
                    "facetFilters": [],
                    "params": f"hitsPerPage={hits_per_page}"
                }
            ]
        })
