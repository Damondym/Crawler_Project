import requests
from urllib.parse import quote
import json
from bs4 import BeautifulSoup
import csv
import time

def get_danmu_by_searchKey(key):
    list = get_search_list(key)
    for video in list:
        aid = video['aid']
        title = video['title']
        url = video['arcurl']
        print('########## ' + title)
        #获取详细信息
        info = get_detail_info(aid)
        title = info['title']
        cid = info['cid']
        create_time = time.strftime("%Y-%m-%d",time.localtime(info['pubdate']))
        desc = info['desc']
        userName = info['owner']['name']
        userId = info['owner']['mid']
        view = info['stat']['view']
        danmuNum = info['stat']['danmaku']
        reply = info['stat']['reply']
        fav = info['stat']['favorite']
        coin = info['stat']['coin']
        share = info['stat']['share']
        like = info['stat']['like']
        dislike = info['stat']['dislike']
        #获取弹幕
        danmu = get_danmu(cid)
        #获取评论
        comment = get_comment(aid,url)
        for i in danmu:
            f_csv.writerow([title,url,i.get_text()])
        for i in comment:
            f_csv2.writerow([title,i['rpid'],i['content']['message'],i['like'],i['action'],
                             time.strftime("%Y-%m-%d",time.localtime(i['ctime'])),
                             i['member']['uname'],i['member']['mid'],i['member']['sex'],
                             i['member']['level_info']['current_level']])
        f_csv1.writerow([title,aid,cid,create_time,desc,url,userName,userId,view,
                         danmuNum,reply,fav,coin,share,like,dislike])

def get_search_list(key):
    key = quote(key)
    page = 1
    resultList = []
    while True:
        url = 'https://api.bilibili.com/x/web-interface/search/type?context=&page={}&order=&keyword={}&duration=&tids_1=&tids_2=&__refresh__=true&search_type=video&highlight=1&single_column=0&jsonp=jsonp'.format(page,key)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
            'Referer': 'https://search.bilibili.com/all?keyword={}&from_source=nav_search_new'.format(key),
            }
        r = requests.get(url,headers=headers)
        js = json.loads(r.text)
        resultList += js['data']['result']
        if page>1:
            break
        page += 1
    return resultList

def get_detail_info(aid):
    url = 'https://api.bilibili.com/x/web-interface/view?aid={}'.format(aid)
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
        }
    r = requests.get(url,headers=headers)
    js = json.loads(r.text)
    return js['data']

def get_danmu(cid):
    url = 'https://comment.bilibili.com/{}.xml'.format(cid)
    headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
        }
    r = requests.get(url,headers=headers)
    r.encoding = 'utf-8'
    soup = BeautifulSoup(r.text,'html.parser')
    soup = soup.find_all('d')
    return soup

def get_comment(aid,arcUrl):
    page = 1
    replyList = []
    while True:
        url = 'https://api.bilibili.com/x/v2/reply?&jsonp=jsonp&pn={}&type=1&oid={}&sort=2'.format(page,aid)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
            'Referer': arcUrl
            }
        r = requests.get(url,headers=headers)
        r.encoding = 'utf-8'
        js = json.loads(r.text)
        if js['data'] == None:
            break
        elif js['data']['replies'] == None:
            break
        replyList += js['data']['replies']
        page += 1 
    return replyList
    
searchKey = '国双'
with open(searchKey + '_danmu.csv','w',newline='',encoding = 'utf-8-sig')as f:
    f_csv = csv.writer(f)
    f_csv.writerow(['视频名称','url','弹幕'])
    with open(searchKey + '_info.csv','w',newline='',encoding = 'utf-8-sig')as f1:
        f_csv1 = csv.writer(f1)
        f_csv1.writerow(['视频名称','aid','cid','发布时间','描述','url',
                         '用户名','用户ID','观看数','弹幕数','评论数','收藏数',
                         '打赏金币数','分享数','点赞数','不认同数'])
        with open(searchKey + '_comment.csv','w',newline='',encoding = 'utf-8-sig')as f2:
            f_csv2 = csv.writer(f2)
            f_csv2.writerow(['视频名称','评论ID','评论内容','点赞数','不认可数',
                             '发表时间','用户名字','用户ID','性别','会员等级'])
            get_danmu_by_searchKey(searchKey)




