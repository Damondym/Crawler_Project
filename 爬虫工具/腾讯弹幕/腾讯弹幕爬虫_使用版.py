import json
import requests
import re
from pymongo import MongoClient
from bs4 import BeautifulSoup
import csv
'''
1、根据url获取lid，cid，vid。
2、根据lid，cid，vid获取targetid。
3、根据targetid获取弹幕。
'''
def craw_danmu_by_url(name,url):
    print('------------开始  '+name)
    lid,cid,vid = get_lid_cid_vid(url)
    targetid = get_targetid(lid,cid,vid)
    get_danmu(targetid,name)

def get_lid_cid_vid(url):
    #getting lid,cid,vid
    print("getting lid,cid,vid")
    urlList = url.split('/')
    cid = urlList[-2]
    vid = urlList[-1].split('.')[0]
    r = requests.get(url)
    soup = BeautifulSoup(r.text,'html.parser')
    href = soup.find('h2',{'class':'player_title'}).find('a')['href']
    lid = href.split('/')[-1].split('.')[0]
    return lid, cid, vid
    

#lid标记不同节目，vid和cid标记不同集，targetid用于字幕标记
def get_targetid(lid,cid,vid):
    #getting targetid
    print("getting targetid")
    url = 'https://access.video.qq.com/danmu_manage/regist?vappid=97767206&vsecret=c0bdcbae120669fff425d0ef853674614aa659c605a613a4&raw=1'
    headers = {
        'User-Agent':"PostmanRuntime/7.19.0",
        'Postman-Token':'ecb9a8ff-480b-4c63-af22-da18d327375d',
        'Host':'access.video.qq.com',
        'Content-Type':'application/json',
        'Accept':'*/*',
        'Cache-Control':'no-cache',
        'Accept-Encoding':'gzip, deflate',
        'Connection':'keep-alive'
        }
    payload ={"wRegistType":2,"vecIdList":[vid],"wSpeSource":0,"bIsGetUserCfg":1,"mapExtData":{vid:{"strCid":cid,"strLid":lid}}}
    r=requests.post(url,headers=headers,data=json.dumps(payload))
    id_compile = re.compile("targetid=([\d]*)&vid")
    targetid = id_compile.findall(r.text)
    return targetid[0]

def get_danmu(targetid,name):
    print('getting danmu')
    with open(name+".csv","w",newline='',encoding = 'utf-8-sig') as csvfile: 
        writer = csv.writer(csvfile)
        writer.writerow(['commentID','content','headurl','opername','rich_type',
                         'timepoint','upcount','vip_degree'])
        timestamp = 0
        while True:
            if timestamp % 10 == 0:
                print("page"+str(timestamp))
            #在js里面
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
                print('!!!!fault in gettint danmu')
                print(content)
            else:
                if len(comments) == 0:
                    break
                for comment in comments:
                    writer.writerow([comment['commentid']+"#",comment['content'],comment['headurl'],
                                     comment['opername'],comment['rich_type'],comment['timepoint'],
                                     comment['upcount'],comment['uservip_degree']])
                timestamp += 1

### 运行程序，name为输出文件名，url为视频网址）
craw_danmu_by_url(name = "test",url = "https://v.qq.com/x/cover/v9pqco6dghrs8gj/c0023i8fpm4.html?")
