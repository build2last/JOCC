# coding:utf-8
# REST practice for Qzone Liker bot to activate program

import os
import random
import json
import time
import threading
import MySQLdb
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.options import define, options
import conf

define("port", default=conf.WEBPORT, help="run on the given port", type=int)
WORKERS_INFO = {}

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        USER_LIST = ["1","2"]
        self.render('index.html', uidlist=USER_LIST)

class SendWorkHandler(tornado.web.RequestHandler):
    def get(self, input):
        task_num = int(self.get_argument('num', '100'))
        task_num = 500 #DEBUG
        conn = MySQLdb.connect(host=conf.HOST, user=conf.USER, passwd=conf.PASS, db=conf.DB_NAME, port=conf.DBPORT, charset='utf8')
        cursor = conn.cursor()
        query_sql = "SELECT mid, url FROM task WHERE status=0 LIMIT %d"%task_num
        cursor.execute(query_sql)
        tasks = cursor.fetchall()
        self.set_header('Content-Type', 'application/json; charset=UTF-8')
        self.write(json.dumps( {"tasks":[{"mid":i[0], "url":i[1]} for i in tasks]} ))
        for task in tasks:
            update_sql = "UPDATE task SET status = 1 WHERE mid = %s"
            cursor.execute(update_sql,(task[0],))
        conn.commit()
        conn.close()
    
    def post(self, input):
        #TODO:May Connection Pool be helpful to handle frequent transaction.
        conn = MySQLdb.connect(host=conf.HOST, user=conf.USER, passwd=conf.PASS, db=conf.DB_NAME, port=conf.DBPORT, charset='utf8')
        cursor = conn.cursor()
        mids = self.get_argument('mid')
        if isinstance(mids, str):
            param = eval(mids)
        for mid in param:
            update_sql = "UPDATE task SET status = 2 WHERE mid = %s"
            cursor.execute(update_sql,(mid,))
        conn.commit()
        conn.close()
        self.write('Database has been updated!')       

class WorkerStatusHandler(tornado.web.RequestHandler):
    """Listen to heart beat 显示并更新 worker 的状态信息"""
    def get(self, input):
        global WORKERS_INFO
        workers_info = WORKERS_INFO
        wid = self.get_argument('wid', '')
        if wid:
            worker_info = workers_info.get(wid, "")
            if worker_info:
                self.write(worker_info)
            else:
                self.write("Not found")
        else:
            self.render('index.html', workers = [{"wid":i, "status":workers_info[i]["status"], "work_load":workers_info[i].get("work_load", "")} for i in workers_info])
    
    def post(self, input):
        # The server will Default to set client ip as worker id.
        wid = self.get_argument('wid', '')
        ip = self.request.remote_ip
        if not wid:
            wid = ip
        worker_info = json.loads(self.get_argument('worker_info').replace("'", "\""))
        global WORKERS_INFO
        WORKERS_INFO[wid] = worker_info
        self.write('OK')

def timer_work(time_delta=120):
    # Refresh workers' status
    global WORKERS_INFO
    WORKERS_INFO = {}
    t = threading.Timer(time_delta, timer_work, (time_delta,))
    t.start()

def start_server():
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers=[(r'/', IndexHandler),
            (r'/worker/task(.*?)', SendWorkHandler),
            (r'/worker/status(.*?)', WorkerStatusHandler),
        ],
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        debug=True
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    t = threading.Thread(target=timer_work, args=(120,))
    t.start()
    t.join()
    start_server()

