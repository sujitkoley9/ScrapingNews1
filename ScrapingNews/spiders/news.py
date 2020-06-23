# -*- coding: utf-8 -*-
import scrapy
from time import sleep
from scrapy import Spider
from selenium import webdriver
from scrapy.selector import Selector
from scrapy.http import Request
from selenium.common.exceptions import NoSuchElementException
from ScrapingNews.items import ScrapingnewsItem
from w3lib.html import replace_escape_chars
import datefinder
import re
import configparser

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC




class NewsSpider(scrapy.Spider):
    name = 'news'

    start_urls = ['https://coloradosun.com/']
    allowed_domains = ['coloradosun.com']

    no_of_pages = 2

    def start_requests(self):
        self.driver = webdriver.Chrome('chromedriver')
        self.driver.get(self.start_urls[0])

        cnt = 1
        while cnt <= self.no_of_pages:
            try:
                next_page = self.driver.find_element_by_xpath(
                    '//div[@class="content-list__more-button-wrapper___plob2 content-list__more-button-wrapper"]/ \
                button[@class="content-list__load-more-button___2UuAm content-list__load-more-button button-secondary-light"]')
                sleep(10)
                self.logger.info('Sleeping for 10 seconds.')
                next_page.click()

                cnt += 1
            except NoSuchElementException:
                self.logger.info('No more pages to load.')

                break
        source_page = self.driver.page_source
        self.driver.quit()
        yield Request(self.start_urls[0],  callback=self.parse_news, meta={'source_page': source_page
                                                                  })

    def parse_news(self, response):

        source_page = response.meta['source_page']
        sel = Selector(text=source_page)
        news_url_list = sel.xpath(
            '//h2[@class="river__title___krYaD river__title" or @class="card__title___W5a0A card__title"]/a/@href').extract()

        for url_item in news_url_list:
            yield Request(url=url_item,  callback=self.parse_news_in_details, meta={'url': url_item
                                                                                    })



    def parse_news_in_details(self, response):
        url = response.meta['url']
        try:
            news = response.xpath(
                '//div[@class="body-content__wrapper___1nN2E body-content__wrapper rich-text body-content__sidebar___3Bplp body-content__sidebar"]/div[@id="pico"]/p/text()').extract()

            ScrapingnewsItem_data = ScrapingnewsItem()
            ScrapingnewsItem_data['url'] = url
            ScrapingnewsItem_data['news_content'] = news
            yield ScrapingnewsItem_data

        except :
           pass


