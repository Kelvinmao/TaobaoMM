#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-06-15 10:48:25
# Project: taobaomm_v2

from pyspider.libs.base_handler import *
import os

PAGE_NUM=1
MAX_PAGE=30
DIR_PATH='/home/kelvinmao/Music/'

class Handler(BaseHandler):
    crawl_config = {
    }
    def __init__(self):
        self.base_url='https://mm.taobao.com/json/request_top_list.htm?page='
        self.page_num=PAGE_NUM
        self.max_page=MAX_PAGE
        self.deal=Deal()

    @every(minutes=24 * 60)
    def on_start(self):
        while self.page_num<=self.max_page:
            url=self.base_url+str(self.page_num)
            print url
            self.crawl(url, callback=self.index_page)
            self.page_num+=1

    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
        for each in response.doc('.lady-name').items():
            self.crawl(each.attr.href, callback=self.detail_page, fetch_type='js')

    @config(priority=2)
    def detail_page(self, response):
        domain = response.doc('.mm-p-domain-info li > span').text()
        if domain:
            domain_name = 'https:' + domain
            self.crawl(domain_name, callback=self.domain_page)

    def domain_page(self, response):
        name=response.doc('.mm-p-model-info-left-top dd > a').text()
        dir_path=self.deal.mkDIR(name)
        brief=response.doc('.mm-aixiu-content').text()
        if dir_path:
            imgs=response.doc('.mm-aixiu-content img').items()
            count=1
            self.deal.save_brief(brief,name,dir_path)
            for img in imgs:
                url = img.attr.src
                if url:
                    extension=self.deal.getextension(url)
                    file_name=name+str(count)+'.'+extension
                    #self.deal.save_Img(img.attr.src,file_name)
                    count += 1
                    self.crawl(img.attr.src, callback=self.save_img, save={'save_path':dir_path,'file_name':file_name})

    def save_img(self,response):
        content=response.content
        dir_path=response.save['save_path']
        file_name=response.save['file_name']
        file_path=dir_path+'/'+file_name
        self.deal.save_Img(content,file_path)

class Deal:
    def __init__(self):
        self.dir_path=DIR_PATH
        if not self.dir_path.endswith('/'):
            self.dir_path=self.dir_path+'/'
        if not os.path.exists(self.dir_path):
            os.makedirs(self.dir_path)

    def mkDIR(self,name):
        name=name.strip()
        #dir_name=self.dir_path+'/'+name
        dir_name=self.dir_path+name
        exists=os.path.exists(dir_name)
        if not exists:
            os.makedirs(dir_name)
            return dir_name
        else:
            return dir_name

    def save_Img(self,content,file_name):
        file=open(file_name,'wb')
        file.write(content)
        file.close()

    def save_brief(self,brief,name,path):
        file_name=path+'/'+name+'.txt'
        file=open(file_name,'w+')
        file.write(brief.encode('utf-8'))
        file.close()

    def getextension(self,url):
        extension=url.split('.')[-1]
        return extension

