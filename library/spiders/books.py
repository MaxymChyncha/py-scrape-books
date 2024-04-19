import re

import scrapy
from scrapy.http import Response

from library.items import Book


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        book_detail_urls = response.css(".product_pod > h3 > a")
        yield from response.follow_all(book_detail_urls, self._get_one_book)

        next_page = response.css(".next > a::attr(href)").get()

        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)

    @staticmethod
    def _get_numeric_amount(amount: str) -> int:
        return int(re.search(r"\d+", amount).group())

    @staticmethod
    def _get_numeric_rating(rating: str) -> int:
        numbers = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5,
        }
        return numbers.get(rating)

    def _get_one_book(self, response: Response):
        return Book(
            title=response.css(".product_main > h1::text").get(),
            price=float(response.css("p.price_color::text").get().replace("£", "")),
            amount_in_stock=self._get_numeric_amount(response.css("p.instock.availability").get()),
            rating=self._get_numeric_rating(response.css('p.star-rating::attr(class)').get().split()[1]),
            category=response.css(".breadcrumb > li > a::text").getall()[2],
            description=response.css(".product_page > p::text").get(),
            upc=response.css("table.table-striped td::text")[0].get()
        )
