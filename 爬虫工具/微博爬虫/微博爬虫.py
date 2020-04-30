import requests
from copyheaders import headers_raw_to_dict
from bs4 import BeautifulSoup
import sys
import json
from urllib.parse import quote
from pymongo import MongoClient
import re
import datetime
import csv
import random
import time

def get_weibo_by_key_time(key,beginDate,endDate,gap,cookie):
    ip = get_new_ip()
    print('begin ' + key)
    with open(key+'.csv','w',newline='',encoding = 'utf-8-sig')as f:
        f_csv = csv.writer(f)
        header = ['mid','用户名','发文时间','内容','转发数','评论数','点赞数']
        f_csv.writerow(header)
        endDate += datetime.timedelta(days=1)
        while beginDate < endDate:
            date = beginDate + datetime.timedelta(days=gap-1)
            if date >= endDate:
                date = endDate + datetime.timedelta(days=-1)
            next = 1
            print('from ' + beginDate.strftime("%Y-%m-%d")+' to '+date.strftime("%Y-%m-%d"))
            while next:
                if next % 10 == 0:
                    time.sleep(1)
                url = 'https://s.weibo.com/weibo?q={}&typeall=1&suball=1&timescope=custom:{}:{}&Refer=g&page={}'.format(key,beginDate.strftime("%Y-%m-%d"),date.strftime("%Y-%m-%d"),next)
                headers = {
                    'Cookie':cookie,
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36',
                }
                weiboList = None
                while True:
                    try:
                        proxies = {"http": ip}
                        r = requests.get(url,headers = headers,proxies = proxies)
                        soup = BeautifulSoup(r.text,'html.parser')
                        if '抱歉，未找到“' + key + '”相关结果' in soup.get_text():
                            break
                        weiboList = soup.find_all('div',{'action-type':'feed_list_item'})
                        if len(weiboList) > 0:
                            break
                    except:
                        print(url)
                        print(r.text)
                        ip = get_new_ip()
                        time.sleep(5)
                if weiboList == None:
                    print('######no weibo in'+beginDate.strftime("%Y-%m-%d") + ' to ' + date.strftime("%Y-%m-%d"))
                    next = None
                else:
                    print('#######' + str(next) + '  ' + str(len(weiboList)))
                    for weibo in weiboList:
                        mid = str(weibo['mid']) + '#'
                        name = weibo.find('a',{'class':'name'})['nick-name']
                        content = weibo.find('p',{'class':'txt'}).get_text().translate(dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd))
                        createTime = re.findall('(\d*[年]?\d+月\d+日)',weibo.get_text())[0]
                        weibo = weibo.find('div',{'class':'card-act'})
                        try:
                            forward = weibo.find('a',{'action-type':'feed_list_forward'}).get_text()[3:]
                            if forward == ' ':
                                forward = '0'
                            comment = weibo.find('a',{'action-type':'feed_list_comment'}).get_text()[2:]
                            if comment == ' ':
                                comment = '0'
                            like = weibo.find('a',{'action-type':'feed_list_like'}).find('em').get_text()
                            if like == '':
                                like = '0'
                            f_csv.writerow([mid,name,createTime,content,forward,comment,like])
                        except:
                            print('error'+name)
                            continue    
                    try:
                        test = soup.find('a',{'class':'next'})['href']
                        next += 1
                        if next > 50:
                            next = None
                    except:
                        next = None
            beginDate += datetime.timedelta(days=gap)

def get_user_weibo(name,uid,conid,lastMonth):
    nowMonth = datetime.date.today().month
    beginMonth = (nowMonth - lastMonth -1) % 12
    pre = ''
    if len(str(beginMonth)) == 1:
        pre = '0'
    global ip
    sinid = ''
    result = []
    while True:
        print(sinid)
        url = 'https://m.weibo.cn/api/container/getIndex?uid={}&luicode=10000011&containerid={}&since_id={}'.format(uid,conid,sinid)
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
                print(ip)
                print(r.text)
                ip = get_new_ip()
                time.sleep(5)
        sinid = js['data']['cardlistInfo']['since_id']
        cards = js['data']['cards']
        for weibo in cards:
            try:
                weibo = weibo['mblog']
            except:
                print(weibo)
                continue
            ## 修改创建时间
            weibo['created_at'] = transfer_time(weibo['created_at'])
            db[name].insert_one(weibo)
        create_time = cards[len(cards)-1]['mblog']['created_at']
        if '2019-'+pre+str(beginMonth) in create_time or '2019-'+pre+str((beginMonth-1)%12) in create_time or '2019-'+pre+str((beginMonth-2)%12) in create_time:
            break
        print(cards[len(cards)-1]['mblog']['created_at'])
        time.sleep(3)

    
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
    page = 1
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
                ip = get_new_ip()
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
            ip = get_new_ip()
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
            return str(datetime.date.today().year) + '-' + str(datetime.date.today().month) + '-' + str(datetime.date.today().day)
        elif '小时前' in time:
            nowHour = datetime.datetime.now().hour
            if nowHour >= int(re.findall('(\d*)小时前',time)[0]):
                return str(datetime.date.today().year) + '-' + str(datetime.date.today().month) + '-' + str(datetime.date.today().day)
            else:
                return str(datetime.date.today().year) + '-' + str(datetime.date.today().month) + '-' + str(datetime.date.today().day-1)
        elif '昨天' in time:
            return str(datetime.date.today().year) + '-' + str(datetime.date.today().month) + '-' + str(datetime.date.today().day-1)
        elif '前天' in  time:
            return str(datetime.date.today().year) + '-' + str(datetime.date.today().month) + '-' + str(datetime.date.today().day-2)
        else:
            return time

def get_ip():
    url = 'http://www.89ip.cn/tqdl.html?api=1&num=1000&port=&address=&isp='
    r = requests.get(url)
    ip = re.findall('([\d\.\:]+)<br>?',r.text)
    return ip

def get_new_ip():
    url = 'https://ip.jiangxianli.com/api/proxy_ip'
    r = requests.get(url)
    js = json.loads(r.text)
    return js['data']['ip']+':'+js['data']['port']

#ipList = get_ip()

ip = get_new_ip()
conn=MongoClient('127.0.0.1', 27017)
#获取一个用户近n个月的所有微博（数据结果在mongoDB）
#db= conn.WeiBoUser
#get_user_weibo('YTG电竞俱乐部2','6134425922','1076036134425922',6)
#根据关键字获取所有微博(包含评论、转发数据)（数据结果在mongoDB）
#db= conn.WeiBo
#get_hotinfo_by_key('国双')
#根据关键字获取指定时间内的所有微博（每天最多50页+只包含互动量数据）（数据结果在“关键字.csv")
#get_weibo_by_key_time(key=key,beginDate=datetime.datetime(2020,2,20),endDate=datetime.datetime(2020,4,26),gap=1,cookie = "SINAGLOBAL=2023608972231.7717.1496907595436; _s_tentry=passport.weibo.com; Apache=5892249541863.881.1586318050553; ULV=1586318050594:47:2:1:5892249541863.881.1586318050553:1585816475448; login_sid_t=68403f793c0bf36f182537a3305adb76; cross_origin_proto=SSL; SSOLoginState=1588131931; un=damon_dym@163.com; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5KvlnH70YE8OXQn19HpUnb5JpX5KMhUgL.FoMXe0zcSK-ceh22dJLoIEXLxKnLBKqL1h2LxK-L1K2LB.BLxK-L1K-L122LxKnLBKqL1h2LxK-L1K2LB.Bt; ALF=1619761077; SCF=AmQ19DuoUQIpk7PYyXKk8DLtdiXZHKpe3fpjJF7CgfmBLZLjWtmQ-u2OHvVnNzvOuF-GOe65UxpInxWnwNvQ5Bw.; SUB=_2A25zrhQTDeRhGeFK6FAX9SvKyz2IHXVQ2gLbrDV8PUNbmtANLVDBkW9NQ2YicUtEUr8SoNuE1DPGjfEdXX3EkuEu; SUHB=010WfjB77eURwR; wvr=6; UOR=,,login.sina.com.cn; webim_unReadCount=%7B%22time%22%3A1588225271252%2C%22dm_pub_total%22%3A0%2C%22chat_group_client%22%3A0%2C%22chat_group_notice%22%3A0%2C%22allcountNum%22%3A38%2C%22msgbox%22%3A0%7D")
