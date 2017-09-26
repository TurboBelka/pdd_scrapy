import scrapy

from loginform import fill_login_form
import json

from pdd_scrapy.items import PddScrapyItem


class PdrHscGovSpider(scrapy.Spider):

    name = "pdr"
    allowed_domains = ["http://pdr.hsc.gov.ua"]
    start_urls = [
        "http://pdr.hsc.gov.ua/test-pdd/uk"
    ]

    login_url = "http://pdr.hsc.gov.ua/test-pdd/uk/authorization?target=exam"
    set_category_url = "http://pdr.hsc.gov.ua/set-exam-category"
    start_exam_url = "http://pdr.hsc.gov.ua/test-pdd/uk/exam"
    check_answer_url = "http://pdr.hsc.gov.ua/test-pdd/uk/check-right-answer"
    categories = ["A", "B", "C", "D", "T"]

    login_user = "skripka696@ukr.net"
    login_pass = "asdf123456"

    def start_requests(self):
        # let's start by sending a first request to login page
        yield scrapy.Request(self.login_url, self.login)

    def login(self, response):
        # got the login page, let's fill the login form...
        data, url, method = fill_login_form(response.url, response.body,
                                            self.login_user,
                                            self.login_pass)

        # and send a request with our login data
        return scrapy.FormRequest(url, formdata=dict(data), dont_filter=True,
                                  method=method, callback=self.set_exam_category)

    def set_exam_category(self, response):
        for category in self.categories:
            form_data = dict(categoryName=category)
            yield scrapy.FormRequest(self.set_category_url, formdata=form_data,
                                     callback=self.start_exam,
                                     meta={'category': category},
                                     dont_filter=True)

    def start_exam(self, response):
        yield scrapy.Request(self.start_exam_url, self.parse, dont_filter=True,
                             meta=response.meta)

    def get_correct_answer(self, response):
        question = response.meta.get('question')
        question['correct_answer'] = json.loads(response.body.decode('utf-8'))['right']
        item = PddScrapyItem(question)
        yield item

    def parse(self, response):
        qs_selector = "//div[@class='questions']/div[contains(@class,'question')]"
        questions = response.xpath(qs_selector)

        if not questions:
            return

        for question in questions:
            question_data = {}
            qs_answers = []

            question_data['categories'] = [response.meta.get('category')]
            question_data['question_id'] = question.xpath('@id').extract_first()
            question_data['question'] = question.xpath('div[contains(@class, "text_question")]/h1/text() |'
                                            ' div[contains(@class, "text_question")]/span/text()').extract_first()
            question_data['image'] = question.xpath('div[contains(@class, "image") and not(contains(@class, "image_2"))]/img/@src').extract_first()

            answer_for_send = None
            question_link_id = question.xpath('@data-link_id').extract_first()
            question_number = 'question_number_{}'.format(question_link_id)

            answers = question.xpath('ul[contains(@class, "answers")]/li')
            for answer in answers:
                answer_id = answer.xpath('input/@value').extract_first()
                answer_for_send = answer_id
                answer_text = answer.xpath('label/text()').extract_first()
                qs_answers.append({answer_id: answer_text})

            question_data['answers'] = qs_answers

            send_answer = {
                'answer': answer_for_send,
                'question': question_number,
                'page': 'exam',
                'last': '0',
                'totalTimer': '1'
            }
            yield scrapy.FormRequest(self.check_answer_url,
                                     formdata=send_answer, dont_filter=True,
                                     meta={'question': question_data},
                                     callback=self.get_correct_answer)
