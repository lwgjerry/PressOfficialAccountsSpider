#coding=utf-8
import scrapy
import re
import sys
import json
reload(sys)
sys.setdefaultencoding("utf8")
from scrapy.selector import Selector
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging
from press.items import PressItem

class PressSpider(scrapy.Spider):
    name = "press"
    allowed_domains = ["mp.weixin.qq.com"]


    def __init__(self):


        self.dic_presses = {
            'renminpress':'人民出版社',
            'jxrmcbs':'江西人民出版社',
            'zjrmcbs':'浙江人民出版社',
            'gdrmcbs':'广东人民出版社',
            'sxrmbook':'陕西人民出版社'
        }

    start_urls = []

    # 拼出搜狗微信页面的URL，把该URL作为起始链接
    def start_requests(self):
        for press_key in self.dic_presses.keys():
            start_url = 'http://weixin.sogou.com/weixin?type=1&query='+press_key+'&ie=utf8&_sug_=n&_sug_type_='
            print '初始请求链接：'+start_url
            yield self.url_request(start_url)

    def url_request(self,start_url):
        return scrapy.Request(start_url, callback=self.parse)


    # 根据起始链接，获取出版社微信列表页面
    def parse(self, response):
        #print response.body
        sel = Selector(response)
        url_title = 'mp.weixin.qq.com'
        url_press_list = sel.xpath('//div[@id="sogou_vr_11002301_box_0"]/@href').extract()
        if url_press_list:
            url_press = url_press_list[0]
            print '获取出版社微信列表页：' + url_press
            yield scrapy.Request(url_press,callback=self.parse_item_list)

    # 根据出版社微信列表页面，获取跳转到每篇文章的URL
    def parse_item_list(self, response):
        sel = Selector(response)
        url_title = 'http://mp.weixin.qq.com'
        js = sel.xpath('//script')
        for item_js in js:
            js_text = str(item_js.extract())
            #print js_text
            r = r'(/s\?timestamp=.*?)&quot;'
            js_urlList = re.findall(r, js_text)
            #print js_urlList
            if js_urlList != []:
                for url_text in js_urlList:
                    url_text = url_text.replace('amp;', '')
                    article_url = url_title + url_text
                    print '获取文章页面：' + article_url
                    yield scrapy.Request(article_url, callback=self.parse_article)

    # 进入文章详情页面之后，抓取所需字段
    def parse_article(self, response):
        sel = Selector(response)
        article_url = response.url
        items = PressItem()
        items['article_url'] = article_url
        press_name_list = sel.xpath('//div[@class="profile_inner"]/strong/text()').extract()
        for press_name in press_name_list:
            items['press_name'] = press_name

        weixin_num_list = sel.xpath('//p[@class="profile_meta"]/span/text()').extract()
        weixin_num = weixin_num_list[0]
        introduction = weixin_num_list[1]
        items['weixin_num'] = weixin_num
        items['introduction'] = introduction

        account_subject_list =sel.xpath('//span[@class="rich_media_meta rich_media_meta_text rich_media_meta_nickname"]/text()').extract()
        items['account_subject'] = account_subject_list[0]

        title_list = sel.xpath('//h2/text()').extract()
        for title in title_list:
            title = title.replace(' ','')
            title = title.replace('\r','')
            title = title.replace('\n', '')
            items['title'] = title
            #print title

        publish_date = sel.xpath('//em[@id="post-date"]/text()').extract()
        items['publish_date'] = publish_date[0]

        # 根据javascript抓取时间戳和随机签名，拼出json页面的URL，获取json页面
        js = sel.xpath('//script')
        timestamp = ''
        signature = ''
        for item_js in js:
            js_text = str(item_js.extract())
            #print js_text

            timestamp_text = js_text.find('timestamp:')
            if timestamp_text > -1:
                timestamp_begin =timestamp_text+11
                timestamp_end=timestamp_begin+10
                timestamp = js_text[timestamp_begin:timestamp_end]
                #print '时间戳：' + timestamp

            signature_text = js_text.find('signature:')
            if signature_text > -1:
                signature_begin = signature_text + 11
                signature_end = signature_begin + 172
                signature = js_text[signature_begin:signature_end]
                #print '签名：' + signature
        json_url = 'http://mp.weixin.qq.com/mp/getcomment?src=3&ver=1&timestamp=%s&signature=%s'%(timestamp,signature)
        yield scrapy.Request(json_url, callback=self.parse_json, meta={'item':items})

    # 获取到json页面之后，根据key获取value数据，并将item返回
    def parse_json(self, response):
        dict_json = json.loads(response.body)
        items = response.meta['item']
        for json_test in dict_json:
            if json_test == 'read_num':
                read_num = str(dict_json[json_test])
                #print '阅读数：'+ read_num
                items['read_num'] = read_num

            if json_test == 'like_num':
                like_num = str(dict_json[json_test])
                #print '点赞数：' + like_num
                items['like_num'] = like_num

        for item in items:
            print item
        yield items





# settings = get_project_settings()
# configure_logging(settings)
# runner = CrawlerRunner(settings)
# runner.crawl(PressSpider)
# d = runner.join()
# d.addBoth(lambda _: reactor.stop())
#
# reactor.run()  # the script will block here until all crawling jobs are finished