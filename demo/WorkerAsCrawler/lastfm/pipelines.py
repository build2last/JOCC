# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import time
import urllib
import json
import threading
from scrapy import signals
from scrapy.exporters import CsvItemExporter

# /* Code for distributed crawler
LATEST_TASK_QUEUE = []
TASK_COUNTER = 0
QUE_LOCK = threading.Lock()

def is_need_report_task(tid):
  # 维护最近任务队列，队列长度应接近最大线程数
  global LATEST_TASK_QUEUE, QUE_LOCK, TASK_COUNTER
  QUE_LOCK.acquire()
  if tid not in LATEST_TASK_QUEUE:
    LATEST_TASK_QUEUE.append(tid)
    TASK_COUNTER += 1
    if len(LATEST_TASK_QUEUE) > 50:
      release_tid = LATEST_TASK_QUEUE[0]
      LATEST_TASK_QUEUE = LATEST_TASK_QUEUE[1:]
      QUE_LOCK.release()
      return release_tid
  QUE_LOCK.release()
  return False 
# */


class CSVPipeline(object):
  def __init__(self):
    self.files = {}

  @classmethod
  def from_crawler(cls, crawler):
    settings = crawler.settings
    data_dir_path = settings.get("DATA_DIR", "DATA")
    pipeline = cls()
    crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
    crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
    return pipeline

  def spider_opened(self, spider):
    file = open('DATA/%s_items_%s.tab.csv' %(spider.name, time.strftime('%Y-%m-%d',time.localtime(time.time()))), 'ab+')
    self.files[spider] = file
    self.exporter = CsvItemExporter(file, include_headers_line=False, delimiter='\t')
    self.exporter.fields_to_export = ["mid", "user_name", "cmt", "time"]
    self.exporter.start_exporting()

  def spider_closed(self, spider):
    # 捕捉到爬虫结束的信号后进行一系列处理
    self.exporter.finish_exporting()
    file = self.files.pop(spider)
    file.close()
    # /*
    spider.worker.report_task(LATEST_TASK_QUEUE)
    print("%d/%d tasks have been done!"%(TASK_COUNTER, spider.work_load))
    # */

  def process_item(self, item, spider):
    self.exporter.export_item(item)
    # /*
    # 数据落盘后，视情况向Master反馈任务完成情况
    mid = item["mid"]
    if is_need_report_task(mid):
      spider.worker.worker_info["status"] = spider.name + " is working."
      spider.worker.report_task([mid])
    # */
    return item

class LastfmPipeline(object):
    def process_item(self, item, spider):
        return item