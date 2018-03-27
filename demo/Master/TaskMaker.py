# coding:utf-8

import time
import MySQLdb
import conf
import Server

# Another way to load data to MySQL:
# load data infile "C://ProgramData/MySQL/MySQL Server 5.7/Uploads/track_info_url_0_part0.txt" ignore into table develop.task(mid, url);
# doing: load data infile "C://ProgramData/MySQL/MySQL Server 5.7/Uploads/track_info_url_1_part1.txt" ignore into table develop.task(mid, url);

class Master:
    def __init__(self):
        CREATE_TABLE_SQL = (
        """CREATE TABLE IF NOT EXISTS `task` ( 
            `mid` varchar(50) NOT NULL, 
            `status` tinyint(1) NOT NULL DEFAULT '0' COMMENT '0:未分配 1:已分配未反馈 2:已完成',
            `worker` varchar(45) DEFAULT NULL, 
            `url` varchar(600) NOT NULL, 
            PRIMARY KEY (`mid`) ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Give out tasks for distributed crawler.';""")
        # Create table in MySQL
        conn = MySQLdb.connect(host=conf.HOST, user=conf.USER, passwd=conf.PASS, db=conf.DB_NAME, port=conf.DBPORT, charset='utf8')
        cursor = conn.cursor()
        cursor.execute(CREATE_TABLE_SQL)
        conn.commit()
        conn.close()
        self.mid = set()
        self.urls = set()

    def generate_task(self, task_file):
        """Promise to provide data with corrent format"""
        with open(task_file) as fr:
            while fr:
                task = fr.readline().strip().split("\t")
                if '' not in task:
                    yield(task)
                else:
                    continue

    def load_func(self, conn, items):
        #特点：内存占用小
        cursor = conn.cursor()
        counter = 0
        for item in items:
            try:
                insert_sql = """insert IGNORE into {table_name} ({column1}, {column2}) VALUES (%s, %s)""".format(table_name="task", column1="mid", column2="url")
                cursor.execute(insert_sql, (item[0], item[1]))
                counter += 1
                conn.commit()
            except Exception as e:
                print(e)
        print("Load %d items success"%counter)

    def load_fast(self, conn, items):
        #Fail
        cursor = conn.cursor()
        insert_sql = """insert into {table_name} ({column1}, {column2}) VALUES (%s, %s)""".format(table_name="task", column1="mid", column2="url")
        paras = []
        for i in items:
            if i[0] not in self.mid and i[1] not in self.urls:
                self.mid.add(i[0])
                self.urls.add(i[1])
                paras.append((i[0], i[1]))
        counter = len(paras)
        print(counter)
        try:
            print("inserting")
            for index in range(len(paras))[::10000]:
                para = paras[index:index+10000]
                cursor.executemany(insert_sql, para)
                print("Load items success")
        except Exception as e:
            print(e)     
        conn.commit()
        
    def load_task(self, task_file):
        try:
            conn = MySQLdb.connect(host=conf.HOST, user=conf.USER, passwd=conf.PASS, db=conf.DB_NAME, port=conf.DBPORT, charset='utf8')
            tasks = self.generate_task(task_file)
            self.load_func(conn, tasks)
            #self.load_fast(conn, tasks)
        except Exception as e:
            print(e)
        finally:
            conn.close()
    
def main():
    master = Master()
    task_files = ["track_info_url_5_part0.txt","track_info_url_5_part1.txt","track_info_url_6_part1.txt","track_info_url_8_part0.txt","track_info_url_8_part1.txt","track_info_url_9_part0.txt","track_info_url_9_part1.txt"]
    for task_file in task_files:
        print("Processing %s"%task_file)
        path = r"C:\ProgramData\MySQL\MySQL Server 5.7\Uploads\\" + task_file
        master.load_task(path)

if __name__ == '__main__':
    tick = time.time()
    main()
    tock = time.time()
    print("Cost %d s"%(tock - tick))