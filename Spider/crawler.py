# coding:utf8
from datetime import datetime
import hashlib
import random
import urllib
import re
from bs4 import BeautifulSoup
import math
import pymongo
import time

__author__ = 'Jayvee'

import sys

reload(sys)
sys.setdefaultencoding("utf-8")
proxylist = {'http': 'http://127.0.0.1:8087'}

conn = pymongo.Connection("127.0.0.1", 27017)
# print conn.database_names()
db = conn.AppChinaData  # 连接库
# db.authenticate("jayvee", "hejiawei")
# data = {'test': '12312312'}
# print db.collection_names()
appdb = db.AppInfo
urldb = db.URLlist


def crawlApp(url, category=''):
    # 首先第一次爬取，获得总页数和相关信息
    html = urllib.urlopen(url, proxies=proxylist).read()
    # html = urllib.urlopen(url).read()
    soup = BeautifulSoup(html)
    # print html
    app_url = url
    url_md5 = hashlib.md5(url).hexdigest()
    msg = soup.select('div.msg')
    app_msg = ''
    if len(msg) > 0:
        app_msg = str(soup.select('div.msg')[0].span.text)
    temp = soup.select('div.main-info')[0].select('a.check-all-remark')[0].text
    match = re.compile('\d+').findall(temp)
    comment_count = int(match[0])
    # 获取应用详情
    app_detail = soup.select('div.app-detail')[0]
    app_name = str(app_detail.select('div.msg')[0].h1.text)
    print '爬取的应用：', app_name
    other_info_temp = soup.select('div.detail-app-other-info')[0]
    other_info = []
    for x in other_info_temp.select('li'):
        # print x.text
        other_info.append(str(x.text))
    # 爬取标签
    app_tag_temp = soup.select('div.detail-app-tag')[0]
    app_tag = []
    for y in app_tag_temp.select('li'):
        # print y.text
        app_tag.append(str(y.text))
    # print other_info
    # print app_tag
    # 爬取应用简介
    app_intro = str(soup.select('p.art-content')[0].text)


    # 爬取评论
    page_count = int(math.ceil(comment_count / 10.0))
    print '总共', comment_count, '条评论,', page_count, '页'
    resultlist = []
    for page_index in range(1, page_count + 1):
        print '正在爬取第', page_index, '页'
        commurl = url + 'comments_' + str(page_index) + '.html'
        html = urllib.urlopen(commurl, proxies=proxylist).read()
        # html = urllib.urlopen(commurl).read()
        soup = BeautifulSoup(html)
        try:
            items = soup.select('ul.comments-list')[0].select('li')
        except:
            print soup
        print '本页', len(items), '条评论'
        if len(items) == 0:
            break
        for li in items:
            comment_data = {'nickname': str(li.select('h2.comment-nickname')[0].text),
                            'version': str(li.select('span.app-version')[0].text[3::]),
                            'date': datetime.strptime(str(li.select('span.date')[0].text[3::]), '%Y-%m-%d %H:%M:%S'),
                            'phonetype': str(li.select('span.phonetype')[0].text),
                            'comment': str(li.select('p.comment-content')[0].text)
            }
            resultlist.append(comment_data)
        sleepcount = random.random() * 3
        print '睡眠', str(sleepcount), '秒'
        time.sleep(sleepcount)
    info = {'app_name': app_name,
            'app_url': app_url,
            'url_md5': url_md5,
            'app_tag': app_tag,
            'other_info': other_info,
            'app_intro': app_intro,
            'app_msg': app_msg,
            'category': category,
            'comments': resultlist}
    # appdb.insert(info)

    return info


def crawlUrl(starturl, category):
    print '即将爬取：', category
    conn = pymongo.Connection("127.0.0.1", 27017)
    # print conn.database_names()
    db = conn.CrawlData  # 连接库
    urldb = db.URLbase
    pageIndex = 1
    pageURL = starturl + '/1_1_' + str(pageIndex) + '_1_0_0_0.html'
    html = urllib.urlopen(pageURL, proxies=proxylist).read()
    soup = BeautifulSoup(html)
    apps = soup.select('ul.app-list')
    applist = apps[0].select('li')
    while len(applist) > 0:
        print '正在爬取 ' + category + ' 类第' + str(pageIndex) + '页APP URL'
        appurllist = []
        # applist = apps[0].select('li')
        appscount = 0
        for li in applist:
            app_name = str(li.select('h1.app-name')[0].text)
            app_url = str(li.a['href'])
            appinfo = {'app_name': app_name, 'app_category': category, 'app_url': app_url,
                       'app_intro': str(li.select('div.app-intro')[0].span.text)}
            if urldb.find_one({'app_url': app_url}) is None:
                appurllist.append(appinfo)
                appscount += 1
                # else:
                # print '重复的URL：', app_url
        print '新增url数：', appscount
        pageIndex += 1
        pageURL = starturl + '/1_1_' + str(pageIndex) + '_1_0_0_0.html'
        # print pageURL
        time.sleep(random.random() * 2)
        html = urllib.urlopen(pageURL, proxies=proxylist).read()
        soup = BeautifulSoup(html)
        apps = soup.select('ul.app-list')
        applist = apps[0].select('li')
        if len(appurllist) > 0:
            urldb.insert(appurllist)
            # applist = apps[0].select('li')
            # appscount = len(applist)
            # for li in applist:
            # print li.a['href']
            # print len(applist)
            # else:
            # break


# crawlUrl('http://www.appchina.com/category/301', '输入法')
# crawlUrl('http://www.appchina.com/category/302', '浏览器')
# crawlUrl('http://www.appchina.com/category/303', '动态壁纸')
# crawlUrl('http://www.appchina.com/category/304', '系统工具')
# crawlUrl('http://www.appchina.com/category/305', '便携生活')
# crawlUrl('http://www.appchina.com/category/306', '影音播放')
# crawlUrl('http://www.appchina.com/category/307', '通话通讯')
# crawlUrl('http://www.appchina.com/category/308', '社交网络')
# crawlUrl('http://www.appchina.com/category/309', '主题插件')
# crawlUrl('http://www.appchina.com/category/310', '拍摄美化')
# crawlUrl('http://www.appchina.com/category/311', '新闻资讯')
# crawlUrl('http://www.appchina.com/category/313', '学习办公')
# crawlUrl('http://www.appchina.com/category/314', '网购支付')
# crawlUrl('http://www.appchina.com/category/315', '金融理财')
# crawlUrl('http://www.appchina.com/category/30', '全部软件')


# crawlUrl('http://www.appchina.com/category/424', '手机网游')
# crawlUrl('http://www.appchina.com/category/411', '益智游戏')
# crawlUrl('http://www.appchina.com/category/412', '射击游戏')
# crawlUrl('http://www.appchina.com/category/413', '策略游戏')
# crawlUrl('http://www.appchina.com/category/414', '动作冒险')
# crawlUrl('http://www.appchina.com/category/415', '赛车竞速')
# crawlUrl('http://www.appchina.com/category/416', '模拟经营')
# crawlUrl('http://www.appchina.com/category/417', '角色扮演')
# crawlUrl('http://www.appchina.com/category/418', '体育运动')
# crawlUrl('http://www.appchina.com/category/419', '棋牌桌游')
# crawlUrl('http://www.appchina.com/category/420', '虚拟养成')
# crawlUrl('http://www.appchina.com/category/421', '音乐游戏')
# crawlUrl('http://www.appchina.com/category/422', '对战格斗')
# crawlUrl('http://www.appchina.com/category/423', '辅助工具')
# crawlUrl('http://www.appchina.com/category/40', '其他游戏')


# result = crawlApp('http://www.appchina.com/app/com.datou.pnzxyxss.test')

print urldb
one = urldb.find_one()
print one
print type(one)
while one is not None:
    # print one['app_url']
    appurl = 'http://www.appchina.com' + one['app_url']+'/'
    category = one['app_category']
    print '准备爬取：'+one['app_name']
    appinfo = crawlApp(appurl, category)
    appdb.insert(appinfo)
    urldb.remove({'app_url': one['app_url']})
    # 为下一轮获取url
    one = urldb.find_one()
    # jsonstr = json.dumps(result)
    # print(type(jsonstr))
    # print(jsonstr)
    # f = open('./file', 'w+')

    # f = codecs.open('./output', 'w', 'utf-8')
    # f.write(jsonstr.encode('utf8'))
    # for key in result:
    # for aa in key:
    # print aa, "::", key[aa]
    # f.write(aa + "::" + key[aa] + '\n')
    # print '=============='
    # f.write("===================================\n")