import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from andbank.items import Article


class AndbankSpider(scrapy.Spider):
    name = 'andbank'
    start_urls = ['https://www.andbank.es/observatoriodelinversor/']

    def parse(self, response):
        links = response.xpath('//a[@class="read-more-button"]/@href').getall()
        yield from response.follow_all(links, self.parse_next)

    def parse_next(self, response):
        yield response.follow(response.url, self.parse_article, dont_filter=True)

        next_article = response.xpath('//a[@rel="next"]/@href').get()
        yield response.follow(next_article, self.parse_next)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = " ".join(response.xpath('//h1//text()').getall())
        if title:
            title = title.strip()

        date = response.xpath('//span[@class="updated"]//text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//div[@class="post-content entry-content"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
