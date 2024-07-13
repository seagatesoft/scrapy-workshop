from scrapy import Request, Spider


class ListAndDetailPagesSpider(Spider):
    name = "list_and_detail_pages"
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response):
        sels = response.css("ol.row > li > article.product_pod")
        for sel in sels:
            book_url = sel.css("h3 > a::attr(href)").get()
            book_url = response.urljoin(book_url)

            yield Request(book_url, callback=self.parse_detail)

        next_page_url = response.css("ul.pager > li.next > a::attr(href)").get()
        if next_page_url:
            next_page_url = response.urljoin(next_page_url)
            yield Request(next_page_url, callback=self.parse)

    def parse_detail(self, response):
        item = {"book_url": response.url}

        breadcrumb_sels = response.css("ul.breadcrumb > li")
        breadcrumbs = []

        for breadcrumb_sel in breadcrumb_sels:
            breadcrumb = {}
            breadcrumb_link = breadcrumb_sel.css("a")

            if breadcrumb_link:
                breadcrumb_url = breadcrumb_link.css("::attr(href)").get()
                breadcrumb_url = response.urljoin(breadcrumb_url)
                breadcrumb["url"] = breadcrumb_url
                breadcrumb["title"] = breadcrumb_link.css("::text").get()
            else:
                breadcrumb["title"] = breadcrumb_sel.css("::text").get()

            breadcrumbs.append(breadcrumb)

        item["breadcrumbs"] = breadcrumbs
        item["title"] = response.css("h1::text").get()
        item["price"] = response.css("p.price_color::text").re_first(r"[0-9.,]+")
        item["availability"] = bool(response.css("p.availability:contains('In stock')"))

        if item["availability"]:
            stock = response.css("p.availability::text").re_first(r"\((\d+) available\)")
            if stock:
                item["stock"] = int(stock)

        img_url = response.css("#product_gallery img::attr(src)").get()
        item["image_url"] = response.urljoin(img_url)
        item["description"] = response.css("#product_description + p::text").get()

        additional_properties = []
        prop_sels = response.css("table.table tr")

        for prop_sel in prop_sels:
            prop = {}
            prop["name"] = prop_sel.css("th::text").get()
            prop["value"] = prop_sel.css("td::text").get()
            additional_properties.append(prop)

        item["additional_properties"] = additional_properties

        return item
