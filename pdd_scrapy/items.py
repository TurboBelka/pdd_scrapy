# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PddScrapyItem(scrapy.Item):
    question_id = scrapy.Field()
    question = scrapy.Field()
    answers = scrapy.Field()
    correct_answer = scrapy.Field()
    image = scrapy.Field()
    categories = scrapy.Field()
