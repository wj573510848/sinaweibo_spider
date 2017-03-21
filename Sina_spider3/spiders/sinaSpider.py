# encoding=utf-8


import sys
import logging
import datetime
import requests
import re
from lxml import etree
from Sina_spider3.weiboID import weiboID
from Sina_spider3.scrapy_redis.spiders import RedisSpider
from scrapy.selector import Selector
from scrapy.http import Request
from Sina_spider3.items import InterestingArea

reload(sys)
sys.setdefaultencoding('utf8')


class Spider(RedisSpider):
    name = "SinaSpider"
    host = "http://weibo.cn"
    redis_key = "SinaSpider:start_urls"
    start_urls = list(set(weiboID))
    logging.getLogger("requests").setLevel(logging.WARNING)  # 将requests的日志级别设成WARNING

    def start_requests(self):
        for uid in self.start_urls:
            #print "UID is:******",uid
            yield Request(url="http://weibo.cn/%s/profile" % uid, callback=self.parse_tweets)

    def parse_tweets(self, response):
        """ 抓取微博数据 """
        selector = Selector(response)
        ID = re.findall('(\d+)/profile', response.url)[0]
        divs = selector.xpath('body/div[@class="c" and @id]')
        for div in divs:
            try:
                my_url=div.xpath('div[2]/a[@class="cc"]/@href').extract()[0]
                #my_url=div.xpath('//div[contains(@id,M_")/div[2]/a[5]/@href').extract()[0]
                #print "This is content url:",my_url              
                if my_url:
                    yield Request(url=my_url, callback=self.parse_comment, dont_filter=True)
            except Exception, e:
                pass

        url_next = selector.xpath('body/div[@class="pa" and @id="pagelist"]/form/div/a[text()="下页"]/@href'.decode('utf8')).extract()
        if url_next:
            yield Request(url=self.host + url_next[0], callback=self.parse_tweets, dont_filter=True)
        else:
            yield Request(url="http://weibo.cn/%s/follow" % ID, callback=self.parse_relationship, dont_filter=True)
            yield Request(url="http://weibo.cn/%s/fans" % ID, callback=self.parse_relationship, dont_filter=True)

    def parse_relationship(self, response):
        """ 打开url爬取里面的个人ID """
        selector = Selector(response)
        if "/follow" in response.url:
            ID = re.findall('(\d+)/follow', response.url)[0]
            flag = True
        else:
            ID = re.findall('(\d+)/fans', response.url)[0]
            flag = False
        urls = selector.xpath('//a[text()="关注他" or text()="关注她"]/@href'.decode('utf')).extract()
        uids = re.findall('uid=(\d+)', ";".join(urls), re.S)
        for uid in uids:
            
            yield Request(url="http://weibo.cn/%s/profile" % uid, callback=self.parse_tweets)

        next_url = selector.xpath('//a[text()="下页"]/@href'.decode('utf8')).extract()
        if next_url:
            yield Request(url=self.host + next_url[0], callback=self.parse_relationship, dont_filter=True)
    def parse_comment(self,response):
        print "This is comment response"
        ReviewItem=InterestingArea()
        selector = Selector(response)
        content = selector.xpath('//div[contains(@id,"M_")]/div/span[@class="ctt"]//text()').extract()
        review = selector.xpath('//div[contains(@id,"C_")]/span[@class="ctt"]//text()').extract()
        #print "This is content:",content
        #print "This is review:",review
        ReviewItem['content']=content
        ReviewItem['review']=review
        ReviewItem['review_url']=response.url
        return ReviewItem
       
