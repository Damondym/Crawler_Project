import requests
from copyheaders import headers_raw_to_dict
from bs4 import BeautifulSoup
import sys
import json
from urllib.parse import quote
from pymongo import MongoClient
import re
import datetime
import random
import time

def get_hotinfo_by_key(searchKey):
    print('---------weiboList')
    begin1 = time.time()
    weiboList = get_hotweibo_by_key(searchKey)
    end1 = time.time()
    print(end1 - begin1)
    for weibo in weiboList:
        print('---------weibo')
        try:
            weibo = weibo['mblog']
        except:
            print(weibo)
            continue
        id = weibo['id']
        ## 修改创建时间
        weibo['created_at'] = transfer_time(weibo['created_at'])
        ## 获取转发内容
        print('----repost')
        begin3 = time.time()
        weibo['repost'] = get_weibo_repost(id)
        end3 = time.time()
        print(end3-begin3)
        ## 获取评论内容
        print('----comment')
        weibo['comment'] = get_weibo_comment(id)
        ## 插入数据
        db[searchKey].insert_one(weibo)
    end2 = time.time()
    print(end2-begin1)
        
def get_hotweibo_by_key(searchKey):
    page = 36
    weibo_list = []
    while True:
        url = 'https://m.weibo.cn/api/container/getIndex?containerid=100103type%3D1%26q%3D{}%26t%3D0&page_type=searchall&page={}'.format(quote(searchKey),page)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        }
        r = requests.get(url,headers)
        try:
            js = json.loads(r.text)
        except:
            print(r.text)
        if js['ok'] == 0:
            break
        weibo_list += js['data']['cards']
        #if page == 10:
        #   break
        page += 1
    return weibo_list

def get_weibo_repost(weiboid):
    repostList = []
    page = 1
    global ip
    while True:
        url = 'https://m.weibo.cn/api/statuses/repostTimeline?id={}&page={}'.format(weiboid,page)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        }
        while True:
            try:
                proxies = {"http": ip}
                r = requests.get(url,headers = headers, proxies=proxies)
                js = json.loads(r.text)
                break
            except:
                print(url)
                print(ip)
                print(r.text)
                ipList.remove(ip)
                ip = random.choice(ipList)
        if js['ok'] == 0:
            break
        for repost in js['data']['data']:
            repost['created_at'] = transfer_time(repost['created_at'])
        repostList += js['data']['data']
        if len(repostList) > 200:
            break
        if page % 20 == 0:
            print(page)
            time.sleep(random.randint(3,5))
        else:
            time.sleep(random.randint(1,3))
        page += 1
    return repostList
        
def get_weibo_comment(weiboid):
    commentList = []
    maxid = 0
    #while True:
    url = 'https://m.weibo.cn/comments/hotflow?id={}&mid={}&max_id={}&max_id_type=0'.format(weiboid,weiboid,maxid)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
    }
    global ip
    while True:
        try:
            proxies = {"http": ip}
            r = requests.get(url,headers = headers, proxies=proxies)
            js = json.loads(r.text)
            break
        except:
            print(url)
            print(ip)
            print(r.text)
            ipList.remove(ip)
            ip = random.choice(ipList)
    if js['ok'] == 0:
        return commentList
        #break
    #if maxid == js['data']['max_id']:
    #    print('last')
    #    break
    #else:
    #    maxid = js['data']['max_id']
    try:
        commentList += js['data']['data']
    except:
        print(js)
    #if len(commentList) > 1000:
    #    break
    return commentList

def transfer_time(time):
    if '-' in time:
        return time
    else:
        if '分钟前' in time or '刚刚' in time:
            return str(datetime.date.today().month) + '-' + str(datetime.date.today().day)
        elif '小时前' in time:
            nowHour = datetime.datetime.now().hour
            if nowHour >= int(re.findall('(\d*)小时前',time)[0]):
                return str(datetime.date.today().month) + '-' + str(datetime.date.today().day)
            else:
                return str(datetime.date.today().month) + '-' + str(datetime.date.today().day-1)
        elif '昨天' in time:
            return str(datetime.date.today().month) + '-' + str(datetime.date.today().day-1)
        elif '前天' in  time:
            return str(datetime.date.today().month) + '-' + str(datetime.date.today().day-2)
        else:
            return time

def get_ip():
    url = 'http://www.89ip.cn/tqdl.html?api=1&num=1000&port=&address=&isp='
    r = requests.get(url)
    ip = re.findall('([\d\.\:]+)<br>?',r.text)
    return ip

conn=MongoClient('127.0.0.1', 27017)
db= conn.WeiBo
ipList = get_ip()
ip = random.choice(ipList)
get_hotinfo_by_key('简爱 奶')
#get_weibo_comment(4445300963762860)

'''
# 基本信息
url = 'https://m.weibo.cn/api/container/getIndex?containerid=100103type%3D60%26q%3D%E7%89%9B%E5%A5%B6%26t%3D0&title=%E7%83%AD%E9%97%A8-%E7%89%9B%E5%A5%B6&cardid=weibo_page&extparam=title%3D%E7%83%AD%E9%97%A8%26mid%3D%26q%3D%E7%89%9B%E5%A5%B6&luicode=10000011&lfid=100103type%3D1%26q%3D%E7%89%9B%E5%A5%B6'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
}
r = requests.get(url,headers)
js = json.loads(r.text)
weibo_list = js['data']['cards']
for weibo in weibo_list:
    mblog = weibo['mblog']
    weiboid = mblog['id']
    time = mblog['created_at']
    likeNum = mblog['attitudes_count']
    commentNum = mblog['comments_count']
    repostNum = mblog['reposts_count']
    user = mblog['user']
    uid = user['id']
    uname = user['screen_name']
    followNum = user['follow_count']
    followerNum = user['followers_count']
    statusNum = user['statuses_count']
'''
'''
# 转发信息
url = 'https://m.weibo.cn/api/statuses/repostTimeline?id=4443618645304108&page=1'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
}
r = requests.get(url,headers)
js = json.loads(r.text)
repost_list = js['data']['data']
for repost in repost_list:
    weiboid = repost['id']
    content = repost['raw_text']
    time = repost['created_at']
    likeNum = repost['attitudes_count']
    commentNum = repost['comments_count']
    repostNum = repost['reposts_count']
    user = repost['user']
    uname = user['screen_name']
    followNum = user['follow_count']
    followerNum = user['followers_count']
    statusNum = user['statuses_count']
'''
'''
# 评论信息
url = 'https://m.weibo.cn/comments/hotflow?id=4443618645304108&mid=4443618645304108&max_id=0&max_id_type=0'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
}
r = requests.get(url,headers)
js = json.loads(r.text)
comment_list = js['data']['data']
for comment in comment_list:
    commentid = comment['id']
    content = comment['text']
    time = comment['created_at']
    likeNum = comment['like_count']
    commentNum = comment['total_number']
    user = comment['user']
    uname = user['screen_name']
    followNum = user['follow_count']
    followerNum = user['followers_count']
    statusNum = user['statuses_count']
'''































'''
def get_user_info():
    url = 'https://m.weibo.cn/api/container/getIndex?type=uid&value=1112928761&containerid=1005051112928761'
    #headerStr = b'user-agent: Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
    headers = headers_raw_to_dict(headerStr)
    r = requests.get(url,headers = headers)
    js = json.loads(r.text)
    follow = js['data']['userInfo']['follow_count']
    follower = js['data']['userInfo']['followers_count']
    status = js['data']['userInfo']['statuses_count']
    return

def get_weiboList_by_key():
    url = 'https://s.weibo.com/weibo?q=%E8%92%99%E7%89%9B&xsort=hot&Refer=hotmore&page=2'
    headerStr = b'''
'''
    Cookie: SINAGLOBAL=2023608972231.7717.1496907595436; login_sid_t=77f4a81063941d07c7fb685fd20094fb; cross_origin_proto=SSL; _s_tentry=www.baidu.com; UOR=,,www.baidu.com; Apache=8020134530361.569.1575009664127; ULV=1575009664132:36:4:3:8020134530361.569.1575009664127:1575005835702; WBtopGlobal_register_version=307744aa77dd5677; SCF=AmQ19DuoUQIpk7PYyXKk8DLtdiXZHKpe3fpjJF7CgfmBEOAQORJySFX2qkf0U3WMuLlk_llsNn9rLOr2QeqZTjA.; SUB=_2A25w5M7mDeRhGedG6VQW9C3LzzuIHXVTk6curDV8PUNbmtAKLWX-kW9NUUfuow7n0cTA8X81FbF4Ocgndq52_hXf; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5s8U2iDC9J14FjdmjTf4zk5JpX5KzhUgL.Fo2ReoqNSheNShM2dJLoIEnLxKqL1h5LB-2LxKML1K.L12eLxKqL1hzLBKeLxKnL1h5L1hHkxGL_; SUHB=0U1IEVVY4E7uGt; ALF=1606545974; SSOLoginState=1575009974; WBStorage=42212210b087ca50|undefined
    User-Agent: Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36
    '''
'''
    headers = headers_raw_to_dict(headerStr)
    r = requests.get(url,headers = headers)
    soup = BeautifulSoup(r.text,'html.parser')
    weibo_list = soup.find_all('div',{'action-type':'feed_list_item'})
    return weibo_list

def get_weibo(weibo):
    non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
    weibo_name = weibo.find('a',{"class":"name"})
    print(weibo_name['nick-name'])
    print(weibo_name['href'][2:])
    weibo_content = weibo.find('p',{'node-type':'feed_list_content'})
    print(weibo_content.get_text().translate(non_bmp_map))
    forward = weibo.find('a',{'action-type':'feed_list_forward'}).get_text()
    comment = weibo.find('a',{'action-type':'feed_list_comment'}).get_text()
    like = weibo.find('a',{'title':'赞'}).get_text()
    print(forward[3:].strip())
    print(comment[3:].strip())
    print(like.strip())
    return
'''
