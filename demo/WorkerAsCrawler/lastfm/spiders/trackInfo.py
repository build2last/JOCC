import time
import json
import scrapy
from scrapy.http import Request
from lastfm.items import CmtItem, TrackItem
from Worker.worker import Worker
import APIRequest

WORKER = Worker("lastfm.trackInfo")
WORKER.heart_beat()

class TrackSpider(scrapy.Spider):
    AUTO_MODE = True
    name = 'trackInfo'
    allowed_domains = ['']
    start_targets = WORKER.get_task(auto=AUTO_MODE, task_type="trackinfo")
    custom_settings = {
        'DOWNLOAD_DELAY' : 0   
    }
    worker = WORKER

    def start_requests(self):
        for mid in self.start_targets:
            url = "http://ws.audioscrobbler.com/2.0/?method=track.getinfo&mbid={mbid}&api_key={key}&format=json".format(mbid=mid, key=APIRequest.get_available_key())
            request = Request(url, callback=self.parse, dont_filter=True)
            request.meta['mid'] = mid
            yield request
    
    def parse(self, response):
        item = TrackItem()
        item["json"] = json.loads(response.body)
        item["mid"] = response.meta["mid"]
        # Worker info update!
        WORKER.update_worker_info_for_one_task()
        yield item
