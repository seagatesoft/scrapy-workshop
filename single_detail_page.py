from scrapy import Spider


class SingleDetailPageSpider(Spider):
    name = "single_detail_page"
    start_urls = ["https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"]

    def parse(self, response):
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
