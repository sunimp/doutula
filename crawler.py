#encoding: utf-8

import urllib.request, urllib.parse, urllib.error
import threading
from bs4 import BeautifulSoup
import requests
import os
import time
 
# 保存路径
DIR_PATH = r"/Users/Sun/Documents/Images"
# 表情链接列表
FACE_URL_LIST = []
# 页面链接列表
PAGE_URL_LIST = []
# 构建2017个页面的链接
BASE_PAGE_URL = 'https://www.doutula.com/photo/list/?page='
for x in range(1, 2017):
    url = BASE_PAGE_URL + str(x)
    PAGE_URL_LIST.append(url)
 
# 初始化锁
gLock = threading.Lock()
 
# 负责从每个页面中提取表情的url
class get_url(threading.Thread):
    def run(self):
        while len(PAGE_URL_LIST) > 0:
            # 在访问PAGE_URL_LIST的时候，加锁
            gLock.acquire()
            page_url = PAGE_URL_LIST.pop()
            # 使用完后释放，方便其他线程使用
            gLock.release()
            response = requests.get(page_url)
            soup = BeautifulSoup(response.content, 'lxml')
            img_list = soup.find_all('img', attrs={'class': 'img-responsive lazy image_dta'})
            gLock.acquire()
            for img in img_list:
                src = img['data-original']
                if not src.startswith('http'):
                    src = 'http:'+ src
                # 把提取到的表情url，添加到FACE_URL_LIST中
                FACE_URL_LIST.append(src)
            gLock.release()
            time.sleep(0.5)
 
# 实际的爬虫入口
# 负责从FACE_URL_LIST提取表情链接，然后下载
class crawler(threading.Thread):
    def run(self):
        print('%s is running' % threading.current_thread)
        while True:
            # 上锁
            gLock.acquire()
            if len(FACE_URL_LIST) == 0:
                # 不管什么情况，都要释放锁
                gLock.release()
                continue
            else:
                # 从FACE_URL_LIST中提取数据
                face_url = FACE_URL_LIST.pop()
                gLock.release()
                filename = face_url.split('/')[-1]
                print('正在爬取'+filename)
                path = os.path.join(DIR_PATH, filename)
                urllib.request.urlretrieve(face_url, filename=path)
 
if __name__ == '__main__':
    # 4个线程，去从页面中爬取表情链接
    for x in range(4):
        get_url().start()
 
    # 5个线程，去从FACE_URL_LIST中提取下载链接，然后下载
    for x in range(5):
        crawler().start()