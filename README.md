# JOCC
To distribute/collect tasks and information on LAN. //Allusion to **Joint Operations Cntrol Center** in military domin.

# 软件简介
Master负责任务的制作和分发，Worker从Master获取任务并交由scrapy完成；

Worker只需搭建起scrapy环境，对操作系统、服务器、Python版本均没有要求；

用户可以通过访问Master的web服务来监视worker运行情况，同时可以通过FTP来获取worker上的数据；

Master对任务进行管理，每一项任务的执行状态都会被记录，无论是待执行、执行中还是已完成，确保没有任务被重复发送；

Worker持续不断地从Master获取任务，同时使用产生器机制又使得任务队列不至于占用太大空间；

Worker在数据成功落盘后才会考虑是否向Server反馈任务完成信号。

Worker的状态信息只通过定时心跳来反馈。

在开工前没有接触过分布式系统，按照我的想法在scrapy的基础上实现了一些功能，目的是方便地将scrapy爬虫扩展成分布式爬虫在多台机器上运行。实际项目中任务数据量在百万量级，而scrapy爬虫本身较为简单。

分布式系统中常见的难题：
1. 负载均衡；
2. 复杂的任务调度；

在我的应用中并不存在。

我主要想解决的问题是：数据（任务完成情况）的一致性。

demo中的Scrapy用于抓取Lastfm歌曲评论信息。

worker 和 master 作为核心亮点功能终点开发，结合scrapy新特性，实现远程对主机进行任务监控，最终任务是实现远程代码部署。

## 启动方法
### Master
目录下运行
> startServer.bat

### Worker
目录下运行
> startCrawler.bat

> startFTP.bat

使用时请注意VPN代理服务器对IP地址的影响。

## 分布式爬虫设计概述

Master中，server提供web接口给worker和用户，taskMaker负责生成任务并导入到数据库中。

Worker中worker模块负责从master获取任务，爬虫调用worker接口获取任务，并通过worker向master反馈任务运行情况。

总之主机之间的直接交互只限于 Server 和 Worker 两个模块，这也体现了我提高代码可维护性的良苦用心。

### Worker
* 开启FTP：供远程访问和下载数据；端口2121
* 开启爬虫：爬虫同时通过 worker 模块提供心跳信息给 master，爬虫默认永续运行

scrapy支持通过telnet控制爬虫

### Master
* 接收 worker 信息 
* 通过 web API向worker提供任务，端口8081

