# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from lastfm.items import CmtItem
from Worker.worker import Worker

# https://www.last.fm/music/Massive+Attack/_/Five+Man+Army/+partial/shoutbox?sort=newest&ajax=1
# https://www.last.fm/music/Massive+Attack/_/Five+Man+Army/+shoutbox?sort=newest&page=2
# https://www.last.fm/music/Massive+Attack/_/Five+Man+Army/+shoutbox?sort=newest
# #[("b30b9943-9100-4d84-9ad2-69859ea88fbb", "https://www.last.fm/music/Massive+Attack/_/Five+Man+Army")]

WORKER = Worker("lastfm.cmtUser")
WORKER.heart_beat()

class CmtuserSpider(scrapy.Spider):
    AUTO_MODE = True
    name = 'cmtUser'
    allowed_domains = ['last.fm']
    start_targets = WORKER.get_task(auto=AUTO_MODE)
    custom_settings = {
        'DOWNLOAD_DELAY' : 0   
    }
    worker = WORKER
    work_load = 0
    def start_requests(self):
        for mid, url in self.start_targets:
            cmt_url = url+"/+shoutbox"
            request = Request(cmt_url+"?sort=newest", callback=self.parse, dont_filter=True)
            request.meta['mid'] = mid
            request.meta['basic_url'] = cmt_url
            yield request

    def parse(self, response):
        li_nodes = response.xpath("//section/ul//li")
        mid = response.meta["mid"]
        self.work_load += 1
        self.worker.update_worker_info({"work_load":self.work_load})
        if not li_nodes:
            return
        for li in li_nodes:
            name = li.xpath('.//h3[@class="shout-user"]/a/text()').extract_first()
            if name:
                item = CmtItem()
                name = name.strip()
                datetime = li.xpath('.//time/@datetime').extract_first().strip()
                cmt = li.xpath('.//div[@class="shout-body"]/p/text()').extract_first().strip()
                item["user_name"] = name
                item["time"] = datetime
                item["mid"] = mid
                item["cmt"] = cmt
                yield item
        next_page_suffix = response.xpath("//li[@class='pagination-next']/a/@href").extract_first()
        if next_page_suffix:
            next_page = response.meta["basic_url"] + next_page_suffix
            yield Request(url=next_page, callback=self.parse, meta=response.meta)
            