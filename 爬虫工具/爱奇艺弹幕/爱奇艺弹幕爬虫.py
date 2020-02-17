import requests
import zlib
import re
import random
import json
from pymongo import MongoClient
from bs4 import BeautifulSoup

def craw_danmuNum_by_tvid(name, tvid):
    print('----------------开始   ' + name)
    albumID, channelId, duration = get_danmu_config(tvid)
    account = get_danmuNum(name,tvid,albumID, channelId, duration)
    print("------"+str(account))

def craw_danmu_by_tvid(name, tvid):
    print('----------------开始   ' + name)
    albumID, channelId, duration = get_danmu_config(tvid)
    get_danmu(name,tvid,albumID, channelId, duration)

def craw_danmu_by_searchKey(search_key):
    name_list, lid_list = get_lid(search_key)
    for i in range(len(name_list)):
        if i<2:
            continue
        name = name_list[i]
        lid = lid_list[i]
        print('----------------开始   ' + name)
        title_list,playUrl_list = get_playUrl(lid)
        for k in range(len(title_list)):
            print('-----开始  ' + title_list[k])
            tvid = get_tvid(playUrl_list[k])
            if tvid:
                albumID, channelId, duration = get_danmu_config(tvid)
                get_danmu(name,tvid,albumID, channelId, duration)
            else:
                print("！！！！！！！！！！！！！FAIL！！！！！！！！！！！")
            

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

def get_playUrl(lid):
    url = 'https://s.video.qq.com/get_playsource?id={}&type=4&data_type=3&range=1-100&otype=json'.format(lid)
    headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
    }
    r = requests.get(url,headers = headers)
    js = json.loads(r.text[13:][:-1])
    video_list = js['PlaylistItem']['videoPlayList']
    title_list = []
    playUrl_list = []
    for video in video_list:
        title_list.append(video['title'])
        playUrl_list.append(video['playUrl'])
    return title_list,playUrl_list

def randomUn(n):
    s = pow(10,n-1)
    e = pow(10,n)-1
    res = random.random() *(e - s) + s
    return res

def get_tvid(playUrl):
    r = requests.get(playUrl)
    try:
        tvid = re.findall(r"param\[\'tvid\'\] = \"(\d+)\"",r.text)[0]
    except:
        return False
    else:
        return tvid

def get_danmu_config(tvid):
    infoUrl = "http://mixer.video.iqiyi.com/jp/mixin/videos/" + tvid
    r = requests.get(infoUrl)
    albumID = re.findall(r"\d+",re.findall(r"\"albumId\":\d+",r.text)[0])[0]
    channelId = re.findall(r"\d+",re.findall(r"\"channelId\":\d+",r.text)[0])[0]
    duration = re.findall(r"\d+",re.findall(r"\"duration\":\d+",r.text)[0])[0]
    return albumID, channelId, duration

def get_danmu(name, tvid,albumID, channelId, duration):
    page = int(duration) // (60*5)+1
    for i in range(1,page+1):
        if i % 10 == 0:
            print(i)
        rn = "0.{}".format(randomUn(16)) 
        url = 'https://cmts.iqiyi.com/bullet/{}/{}/{}_300_{}.z?rn={}&business=danmu&is_iqiyi=true&is_video_page=true&tvid={}&albumid={}&categoryid={}&qypid=01010021010000000000'.format(
            tvid[-4:-2],tvid[-2:],tvid,i,rn,tvid,albumID,channelId)
        r = requests.get(url)
        try:
            res = zlib.decompress(r.content)
        except:
            print(url)
            print(r.content[100:1000])
            return
        res = res.decode('utf-8')
        compile = re.compile("(<bulletInfo>[\s\S]*?</bulletInfo>)")
        danmu_list = compile.findall(res)
        print(len(danmu_list))
        for danmu in danmu_list:
            danmu_json = {}
            content_list = re.findall(">(\S*?)</",danmu)
            try:
                danmu_json["contentId"] = content_list[0]
                danmu_json["content"] = content_list[1]
                danmu_json["parentId"] = content_list[2]
                danmu_json["showTime"] = content_list[3]
                danmu_json["font"] = content_list[4]
                danmu_json["color"] = content_list[5]
                danmu_json["opacity"] = content_list[6]
                danmu_json["position"] = content_list[7]
                danmu_json["background"] = content_list[8]
                danmu_json["contentType"] = content_list[9]
                danmu_json["isReply"] = content_list[10]
                danmu_json["likeCount"] = content_list[11]
                danmu_json["plusCount"] = content_list[12]
                danmu_json["dissCount"] = content_list[13]
                danmu_json["senderAvatar"] = content_list[14]
                danmu_json["uid"] = content_list[15]
                danmu_json["udid"] = content_list[16]
                if len(content_list) > 17:
                    danmu_json["name"] = content_list[17]
                else:
                    danmu_json["name"] = " "
                    print("#")
                #danmu_json = json.dumps(danmu_json)
                db[name].insert_one(danmu_json)
            except:
                print(danmu_json)

def get_danmuNum(name, tvid,albumID, channelId, duration):
    account = 0
    page = int(duration) // (60*5)+1
    for i in range(1,page+1):
        if i % 10 == 0:
            print(i)
        rn = "0.{}".format(randomUn(16)) 
        url = 'https://cmts.iqiyi.com/bullet/{}/{}/{}_300_{}.z?rn={}&business=danmu&is_iqiyi=true&is_video_page=true&tvid={}&albumid={}&categoryid={}&qypid=01010021010000000000'.format(
            tvid[-4:-2],tvid[-2:],tvid,i,rn,tvid,albumID,channelId)
        r = requests.get(url)
        try:
            res = zlib.decompress(r.content)
        except:
            print(url)
            print(r.content[100:1000])
            return
        res = res.decode('utf-8')
        compile = re.compile("(<bulletInfo>[\s\S]*?</bulletInfo>)")
        danmu_list = compile.findall(res)
        account += len(danmu_list)
    return account

conn=MongoClient('127.0.0.1', 27017)
db= conn.IQiYi
# 按关键字搜索爬取一系列视频的弹幕
#craw_danmu_by_searchKey("奇葩说")
# 爬取某个弹幕
#craw_danmu_by_tvid("奇葩说test", "9386529800")




'''
date = "_2019-11-27"
tvList = [
    ["中国梦之声_2019-11-24","9718540700"],
    ["妻子的浪漫日记_2019-11-24","9619901000"],
    ["奇葩说第六季_2019-11-23","9671256700"],
    ["我就是演员_2019-11-23","9681043800"]
    ]
for tv in tvList:
    craw_danmuNum_by_tvid(tv[0]+date, tv[1])

<bulletInfo>
<contentId>1574144727014003648</contentId>
<content>奇葩说可以改名叫相声大会了</content>
<parentId>0</parentId>
<showTime>1</showTime>
<font>20</font>
<color>ffffff</color>
<opacity>1</opacity>
<position>0</position>
<background>0</background>
<contentType>0</contentType>
<isReply>false</isReply>
<likeCount>0</likeCount>
<plusCount>0</plusCount>
<dissCount>0</dissCount>
<userInfo>
<senderAvatar>http://www.iqiyipic.com/common/fix/1541752140.png</senderAvatar>
<uid>1747842941</uid>
<udid>79f85d86d626279736b796785f448ac82016720a</udid>
<name>未知用户</name>
</userInfo>
</bulletInfo>
'''
