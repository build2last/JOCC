# coding:utf-8
import threading
import six.moves.urllib as urllib
import six.moves.urllib.request
import json

MASTER_ADDRESS = "http://58.198.176.33:8081"
TASK_URL = MASTER_ADDRESS + "/worker/task"
HERAT_BEAT_URL = MASTER_ADDRESS+"/worker/status"

class Worker:
    """
    Try to keep Worker thread safe!

    The jobs of Worker includes:
    1. Get tasks from Mater with HTTP；
    2. Sent heart-beat infomation to Master server.
    """
    def __init__(self, name):
        self.name = name
        self.worker_info = {}   # 记录爬虫运行情况
        self.lock = threading.Lock()

    def update_worker_info(self, worker_info):
        self.lock.acquire()
        for key in worker_info:
            self.worker_info[key] = worker_info[key]
        self.lock.release()

    def report_task(self, tids):
        # Report to master about which task has been done
        postdata = urllib.parse.urlencode({"mid":tids}).encode("utf-8")
        req = urllib.request.Request(TASK_URL, postdata)
        staus = urllib.request.urlopen(req).read()
        print(staus)

    def get_task(self, auto=True, num=500):
        """With auto=True the worker instance will continue to get batch tasks from master. 
        So the generator won't start untill Master stop to provide tasks."""
        tasks = json.loads(urllib.request.urlopen(TASK_URL+"?num=%d"%num, timeout=15).read())
        while tasks["tasks"]:
            task = tasks["tasks"].pop()
            yield (task["mid"], task["url"])
        while auto:
            tasks = json.loads(urllib.request.urlopen(TASK_URL+"?num=%d"%num, timeout=15).read())
            if len(tasks["tasks"]) < num:
                auto = False
            while tasks["tasks"]:
                task = tasks["tasks"].pop()
                yield (task["mid"], task["url"])

    def heart_beat(self, time_delta=60):
        """Sent information to master as a timer thread."""
        postdata = urllib.parse.urlencode({"worker_info":self.worker_info}).encode("utf-8")
        url = HERAT_BEAT_URL
        req = urllib.request.Request(url, postdata)
        resp_data = urllib.request.urlopen(req).read()    
        t = threading.Timer(time_delta, self.heart_beat, (time_delta,))
        t.daemon = True
        t.start()
                
def main():
    w = Worker("厉害了")
    t = threading.Thread(target=w.heart_beat, args=(1,), daemon=True)
    t.start()
    t.join()

if __name__ == '__main__':
    main()