from scrapy import Spider


class SingleListPageSpider(Spider):
    name = "single_list_page"
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response):
        rating_map = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5,
        }
        sels = response.css("ol.row > li > article.product_pod")

        for sel in sels:
            item = {"list_url": response.url}

            book_url = sel.css("h3 > a::attr(href)").get()
            item["book_url"] = response.urljoin(book_url)

            img_url = sel.css("div.image_container img::attr(src)").get()
            item["thumbnail_url"] = response.urljoin(img_url)

            item["title"] = sel.css("h3 > a::attr(title)").get()
            item["price"] = sel.css("div.product_price p.price_color::text").re_first(r"[0-9.,]+")

            stock_info = sel.css("div.product_price p.availability:contains('In stock')")
            item["availability"] = bool(stock_info)

            rating_text = sel.css("p.star-rating::attr(class)").re_first(r"star-rating\s+(\w+)")
            if rating_text in rating_map:
                item["rating"] = rating_map[rating_text]

            yield item
