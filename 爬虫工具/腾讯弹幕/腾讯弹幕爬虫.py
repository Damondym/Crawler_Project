import json
import requests
import re
from pymongo import MongoClient
from bs4 import BeautifulSoup

def craw_danmuNum_by_targetid(name, targetid):
    print('------------开始  '+name)
    account = get_danmuNum(name, targetid)
    print('-----' + str(account))

def craw_danmu_by_lid_cid_vid(name,lid,cid,vid):
    print('------------开始  '+name)
    targetid = get_targetid(lid,cid,vid)
    get_danmu(targetid,name)

def craw_danmu_by_lid(lid):
    title_list,cid_list,vid_list = get_cid_vid(lid)
    for k in range(len(title_list)):
        print('-----开始  ' + title_list[k])
        targetid = get_targetid(lid,cid_list[k],vid_list[k])
        get_danmu(targetid,title_list[k])

def craw_danmu_by_searchKey(search_key):
    name_list,lid_list = get_lid(search_key)
    for i in range(len(name_list)):
        name = name_list[i]
        lid = lid_list[i]
        print('----------------开始   ' + name)
        title_list,cid_list,vid_list = get_cid_vid(lid)
        for k in range(len(title_list)):
            print('-----开始  ' + title_list[k])
            targetid = get_targetid(lid,cid_list[k],vid_list[k])
            get_danmu(targetid,name)
            
# 根据关键词获取系列的lid
def get_lid(search_key):
    url = 'https://v.qq.com/x/search/?q={}&stag=0&smartbox_ab='.format(search_key)
    headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
    }
    r = requests.get(url,headers = headers)
    tv_compile = re.compile('data-id="([\d]*)" data-suggest=')
    tvid_list = tv_compile.findall(r.text)
    soup = BeautifulSoup(r.text,'html.parser')
    tvname_list = []
    for tvid in tvid_list:
        tvname_list.append(soup.find('div',{'data-id':tvid}).find('img',{'class':'figure_pic'})['alt'])
    return tvname_list,tvid_list 

# 根据系列的lid获取所有剧集的cid和vid
def get_cid_vid(lid):
    url = 'https://s.video.qq.com/get_playsource?id={}&type=4&data_type=3&range=1-100&otype=json'.format(lid)
    print(url)
    headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
    }
    r = requests.get(url,headers = headers)
    js = json.loads(r.text[13:][:-1])
    video_list = js['PlaylistItem']['videoPlayList']
    title_list = []
    cid_list = []
    vid_list = []
    for video in video_list:
        title_list.append(video['title'])
        cid_list.append(video['id'])
        #vid_compile = re.compile('vid=(\S*)')
        vid_compile = re.compile('vid=(\S*)')
        vid_list.append(vid_compile.findall(video['playUrl'])[0])
    return title_list,cid_list,vid_list

#lid标记不同节目，vid和cid标记不同集，targetid用于字幕标记
def get_targetid(lid,cid,vid):
    url = 'https://access.video.qq.com/danmu_manage/regist?vappid=97767206&vsecret=c0bdcbae120669fff425d0ef853674614aa659c605a613a4&raw=1'
    headers = {
        'User-Agent':"PostmanRuntime/7.19.0",
        'Postman-Token':'ecb9a8ff-480b-4c63-af22-da18d327375d',
        'Host':'access.video.qq.com',
        'Content-Type':'application/json',
        'Accept':'*/*',
        'Cache-Control':'no-cache',
        'Accept-Encoding':'gzip, deflate',
        'Content-Length':'153',
        'Connection':'keep-alive'
        }
    payload ={"wRegistType":2,"vecIdList":[vid],"wSpeSource":0,"bIsGetUserCfg":1,"mapExtData":{vid:{"strCid":cid,"strLid":lid}}}
    r=requests.post(url,headers=headers,data=json.dumps(payload))
    id_compile = re.compile("targetid=([\d]*)&vid")
    targetid = id_compile.findall(r.text)
    return targetid[0]

def get_danmuNum(name, targetid):
    account = 0
    timestamp = 0
    while True:
        url = 'https://mfm.video.qq.com/danmu?otype=json&target_id={}&timestamp={}'.format(targetid,timestamp*30)
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
            'Cache-Control':'no-cache',
        }
        r = requests.get(url,headers = headers)
        content = json.loads(r.text,strict=False)
        try:
            if content['count'] == 0:
                break
            else:
                account += content['count']
                timestamp += 1
                if timestamp % 20 == 0:
                    print(timestamp)
        except:
            print(content)
    return account
    
def get_danmu(targetid,name):
    timestamp = 0
    while True:
        url = 'https://mfm.video.qq.com/danmu?otype=json&target_id={}&timestamp={}'.format(targetid,timestamp*30)
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
            'Cache-Control':'no-cache',
        }
        r = requests.get(url,headers = headers)
        content = json.loads(r.text,strict=False)
        try:
            comments = content['comments']
        except:
            print(content)
        else:
            if len(comments) == 0:
                break
            insert_db(name,comments)
            timestamp += 1
            if timestamp % 20 == 0:
                print(timestamp)

def insert_db(name,comments):
    for comment in comments:
        db[name].insert_one(comment)


conn=MongoClient('127.0.0.1', 27017)
db= conn.TecentVedio
tips = '''
腾讯弹幕爬虫：
1：根据关键字爬取所有相关视频的弹幕。
2：根据该系列的lid爬取所有相关视频的弹幕。
3：根据该视频的lid、cid和vid爬取弹幕。
请输入所需功能的编号:'''
function = input(tips)
if function == '1':
    key = input('请输入关键词:')
    craw_danmu_by_searchKey(key)
elif function == '2':
    key = input('请输入lid:')
    craw_danmu_by_lid(key)
elif function == '3':
    key = input('请输入视频名称（用于存储命名）、lid、cid和vid，以*隔开:')
    keyList = key.split('*')
    craw_danmu_by_lid_cid_vid(keyList[0],keyList[1],keyList[2],keyList[3])

    
    #craw_danmu_by_lid_cid_vid('幸福三重奏 第2季 第5期_1225','85312','mzc002004qwmw0m','p003213fs1b')
    #craw_danmu_by_lid('83823')
    #craw_danmu_by_searchKey('声入人心')
