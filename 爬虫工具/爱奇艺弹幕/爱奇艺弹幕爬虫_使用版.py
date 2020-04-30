import requests
import zlib
import re
import random
import json
from bs4 import BeautifulSoup
import csv
'''
1、根据url获取config(tvid, albumID, channelId, duration)。
2、根据config获取弹幕。
'''

def craw_danmu_by_url(name, url):
    print('----------------开始   ' + name)
    tvid, albumID, channelId, duration = get_danmu_config(url)
    get_danmu(name,tvid,albumID, channelId, duration)

def get_danmu_config(url):
    ##getting config
    '''
    print('getting config')
    infoUrl = "http://mixer.video.iqiyi.com/jp/mixin/videos/" + tvid
    r = requests.get(infoUrl)
    albumID = re.findall(r"\d+",re.findall(r"\"albumId\":\d+",r.text)[0])[0]
    channelId = re.findall(r"\d+",re.findall(r"\"channelId\":\d+",r.text)[0])[0]
    duration = re.findall(r"\d+",re.findall(r"\"duration\":\d+",r.text)[0])[0]
    print('get albumID, channelId, duration')
    return albumID, channelId, duration
    '''
    print('getting config')
    r = requests.get(url)
    tvID = re.findall(r"param\['tvid'\] = \"(\d+)\"",r.text)[0]
    albumID = re.findall(r"param\['albumid'\] = \"(\d+)\"",r.text)[0]
    channelId = re.findall(r"param\['channelID'\] = \"(\d+)\"",r.text)[0]
    duration = re.findall(":video-info=[\s\S]+?\S+\"duration\":(\d+)",r.text)[0]
    return tvID, albumID, channelId, duration

def randomUn(n):
    s = pow(10,n-1)
    e = pow(10,n)-1
    res = random.random() *(e - s) + s
    return res

def get_danmu(name, tvid,albumID, channelId, duration):
    ##getting danmu
    print('getting danmu')
    with open(name+".csv","w",newline='',encoding = 'utf-8-sig') as csvfile: 
        writer = csv.writer(csvfile)
        writer.writerow(['contentID','content','parentID','showTime','isReply',
                         'likeCount','plusCount','dissCount','senderAvatar','uid',
                         'udid','name'])
        page = int(duration) // (60*5)+1
        for i in range(1,page+1):
            if i % 10 == 0:
                print('###page'+str(i))
            rn = "0.{}".format(randomUn(16)) 
            url = 'https://cmts.iqiyi.com/bullet/{}/{}/{}_300_{}.z?rn={}&business=danmu&is_iqiyi=true&is_video_page=true&tvid={}&albumid={}&categoryid={}&qypid=01010021010000000000'.format(
                tvid[-4:-2],tvid[-2:],tvid,i,rn,tvid,albumID,channelId)
            r = requests.get(url)
            try:
                res = zlib.decompress(r.content)
            except:
                ##!!!!!!fault in getting zip
                print('!!!!!!fault in getting zip')
                print(url)
                print(r.content[100:1000])
                return
            res = res.decode('utf-8')
            compile = re.compile("(<bulletInfo>[\s\S]*?</bulletInfo>)")
            danmu_list = compile.findall(res)
            for danmu in danmu_list:
                danmu_json = {}
                content_list = re.findall(">(\S*?)</",danmu)
                try:
                    danmu_json["contentId"] = content_list[0] + '#'#'#'用于防止数字在csv中被省化
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
                    writer.writerow([danmu_json["contentId"],danmu_json["content"],danmu_json["parentId"],danmu_json["showTime"],danmu_json["isReply"],
                                     danmu_json["likeCount"],danmu_json["plusCount"],danmu_json["dissCount"],danmu_json["senderAvatar"],danmu_json["uid"],
                                     danmu_json["udid"],danmu_json["name"]])
                except:
                    ## !!!!fault in danmu_json
                    print('!!!!fault in danmu_json')
                    print(danmu_json)

### 运行程序，name为输出文件名，url为视频网址）
craw_danmu_by_url(name="test", url = "https://www.iqiyi.com/v_19ryi480ks.html")
       
