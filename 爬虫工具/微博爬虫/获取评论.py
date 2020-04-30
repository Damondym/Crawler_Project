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

def get_weibo_comment(weiboid):
    commentList = []
    maxid = 0
    #while True:
    url = 'https://m.weibo.cn/comments/hotflow?id={}&mid={}&max_id={}&max_id_type=0'.format(weiboid,weiboid,maxid)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
    }
    global ipList
    global t
    global choose
    t += 1
    if t == 10:
        t = 0
        #choose = 1 - choose
        choose = random.randint(0,len(ipList)-1)
        time.sleep(3)
    while True:
        try:
            proxies = {"http": ipList[choose]}
            r = requests.get(url,headers = headers, proxies=proxies)
            js = json.loads(r.text)
            break
        except:
            print(url)
            print(ipList[choose])
            print(r.text)
            #if choose == 1:        
            #    ip = get_new_ip()
            #    ipList[1] = ip
            #    choose = 0
            #else:
            #    choose = 1
            ipList.remove(ipList[choose])
            if len(ipList) < 10:
                ipList = get_ip()
            choose = random.randint(0,len(ipList)-1)
            time.sleep(30)
    try:
        return js['data']['data']
    except:
        print('error  '+str(weiboid))
        return None

def get_new_ip():
    url = 'https://www.freeip.top/api/proxy_ip'
    r = requests.get(url)
    js = json.loads(r.text)
    return js['data']['ip']+':'+js['data']['port']

def get_ip():
    url = 'http://www.89ip.cn/tqdl.html?api=1&num=1000&port=&address=&isp='
    r = requests.get(url)
    ip = re.findall('([\d\.\:]+)<br>?',r.text)
    return ip

ip = get_new_ip()
host = '14.23.32.42'
ipList = get_ip()#[host,ip]
choose = 0
t = 0
with open('test.csv',newline='',encoding='UTF-8') as csvfile:
    rows=csv.reader(csvfile)
    with open('f.csv','w',newline='',encoding = 'utf-8-sig')as f:
        f_csv = csv.writer(f)
        header = ['原微博id','评论id','评论时间','正文','回复数量','点赞数量','作者点赞','用户id','用户名','用户性别','用户微博数','用户关注数','用户粉丝数','用户认证标签','用户描述','会员等级']
        f_csv.writerow(header)
        for row in rows:
            mid = row[0][:-1]
            commentNum = row[5]
            if commentNum != ' ':
                print(mid)
                commentList = get_weibo_comment(mid)
                if commentList is not None:
                    for comment in commentList:
                        commentid = comment['id']
                        comment_created_at = comment['created_at']
                        comment_content = BeautifulSoup(comment['text'],'html.parser').get_text()
                        comment_commentNum = comment['total_number']
                        comment_likeNum = comment['like_count']
                        comment_ifAutherLike = comment['isLikedByMblogAuthor']
                        ## 用户数据
                        comment_user = comment['user']
                        comment_userid = comment_user['id']
                        comment_username = comment_user['screen_name']
                        comment_gender = comment_user['gender']
                        comment_weiboNum = comment_user['statuses_count']
                        comment_followNum = comment_user['follow_count']
                        comment_followerNum = comment_user['followers_count']
                        if comment_user['verified']:
                            comment_verified = comment_user['verified_reason']
                        else:
                            comment_verified = ''
                        comment_description = comment_user['description']
                        comment_rank = comment_user['mbrank']    
                        ## 输出数据
                        f_csv.writerow([mid,commentid,comment_created_at,comment_content,comment_commentNum,comment_likeNum,comment_ifAutherLike,
                                         comment_userid,comment_username,comment_gender,comment_weiboNum,comment_followNum,comment_followerNum,comment_verified,comment_description,comment_rank])
            
