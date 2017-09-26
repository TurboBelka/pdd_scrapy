from scrapy.http import FormRequest
from loginform import fill_login_form
import scrapy
import json
from scrapy import Request
#from items import PdrScrapyItem


class PdrSpider(scrapy.Spider):
    name = 'pdr1'
    allowed_domains = ['http://pdr.hsc.gov.ua']
    main_page = "http://pdr.hsc.gov.ua/test-pdd/uk/"
    start_urls = ["http://pdr.hsc.gov.ua/test-pdd/uk/authorization?target=exam"]
    login_user = "skripka696@ukr.net"
    login_pass = "asdf123456"
    search_url = 'https://www.xing.com/search/members?hdr=1&keywords=Serviceleiter&page=%7B%7D'
    count_item = 0
    category_url = 'http://pdr.hsc.gov.ua/get-exam-category'
    exam_url = 'http://pdr.hsc.gov.ua/test-pdd/uk/exam'
    category_choice = {'A', 'B', 'C', 'D'}

    def parse(self, response):
        args, url, method = fill_login_form(response.url, response.body,
                                            self.login_user, self.login_pass)
        return FormRequest(url, method=method, formdata=args,
                           callback=self.confirm_login, dont_filter=True)

    def confirm_login(self, response):
        #TODO: check login confirm
        print(response.url)
        return scrapy.Request(url=self.main_page, callback=self.set_category, dont_filter=True)

    def set_category(self, response):
        print(response.url)
        set_url = "http://pdr.hsc.gov.ua/set-exam-category"
        for category in self.category_choice:

            form_data = {'categoryName': category}
            yield FormRequest(url=set_url, formdata=form_data, callback=self.start_test,
                              meta={'category': category},
                              dont_filter=True)

    def start_test(self, response):
        print(response.url)
        yield Request(url=self.exam_url, meta=response.meta, callback=self.parse_questions, dont_filter=True)

    def parse_questions(self, response):
        print(response.url)
        questions_id = response.xpath('//div[@class="questions"]/div[@class="wrap_pagination"]/ul/li[contains(@class, "numbers")]/@data-link_id').extract()
        questions = response.xpath('//div[@class="questions"]/div[contains(@class, "question")]')

        for question in questions:
            question_data = {}
            answers_data = {}
            question_data['question_id'] = question.xpath('@id').extract_first()
            question_data['question_title'] = question.xpath('div[contains(@class, "text_question")]/h1/text() |'
                                            ' div[contains(@class, "text_question")]/span/text()').extract_first()
            answers = question.xpath('ul[contains(@class, "answers")]/li').extract_first()
            for answer in answers:
                answer_id = answer.xpath('input/@value').extract_first()
                answer_text = answer.xpath('label/text()').extract_first()
                answers_data[answer_id] = answer_text
            #question_data[]



        # question_url = 'http://pdr.hsc.gov.ua/test-pdd/uk/check-for-seo'
        # for question_id in questions_id:
        #     form_data = {'questionPath': '/test-pdd/uk/exam/{}'.format(question_id)}
        #     response.meta['question_id'] = question_id
        #     yield FormRequest(url=question_url, formdata=form_data,
        #                       callback=self.parse_each_question, meta=response.meta, dont_filter=True)

    def parse_each_question(self, response):
        print(response.url)