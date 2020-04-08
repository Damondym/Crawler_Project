import requests
import json
import sys
import csv
import time

def get_kol_info():
    url = 'https://i.snssdk.com/user/profile/homepage/v7/?&user_id=3678162962&request_source=1&active_tab=dongtai&device_id=123&media_id=3678219091'
    headers = {
        'user-agent': 'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Mobile Safari/537.36'
    }
    r = requests.get(url, headers = headers)
    js = json.loads(r.text)
    data = js['data']
    publish_count = data['publish_count']
    following = data['followings_count']
    fans = data['followers_count']
    digg = data['digg_count']
    verified = data['verified_content']
    area = data['area']
    description = data['description']
'''
readyList = [['5872903312','5872903312'],['55533137869','1559820313645058'],['109166144433','1620521944901640'],['82046157597','1590192388066307'],
             ['60803455808','1568093712397313'],['3082675145683747','1633037152982030'],['4175794439','4175794439'],['109168756627','1620526067495944'],
             ['88971900826','1591086763037710'],['62213903835','1570620442550274'],['4086925178','4087963526'],['50019234672','50020509329'],
             ['64376297344','1590192312734727'],['4592579758','0'],['109091690633','1620349156909059']]
'''
readyList = [['111016684338','1624136496150535'],['73815265827','1582640486225933']]
with open('e.csv','w',newline='',encoding = 'utf-8-sig')as f:
    for li in readyList:
        user_id = li[0]
        media_id = li[1]
        f_csv = csv.writer(f)
        header = ['名称','发文数','关注数','粉丝数','获赞数','认证','简介',
                      '文章id','标题','发布时间','评论数','转发数','点赞数']
        f_csv.writerow(header)
        url = 'https://profile.zjurl.cn/user/profile/homepage/v7/?&user_id={}&request_source=1&active_tab=dongtai&device_id=123&media_id={}'.format(user_id,media_id)
        headers = {
            'user-agent': 'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Mobile Safari/537.36'
        }
        r = requests.get(url, headers = headers)
        js = json.loads(r.text)
        data = js['data']
        name = data['screen_name']
        publish_count = data['publish_count']
        following = data['followings_count']
        fans = data['followers_count']
        all_digg = data['digg_count']
        verified = ''#data['verified_content']
        #area = data['area']
        description = data['description']
        times = 7
        offset = '0'
        while times:
            url = 'https://profile.zjurl.cn/api/feed/profile/v1/?category=profile_all&visited_uid={}&stream_api_version=82&request_source=1&offset={}&user_id={}&media_id={}'.format(user_id,offset,user_id,media_id)
            headers = {
                'user-agent': 'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Mobile Safari/537.36',
                'referer': 'https://profile.zjurl.cn/rogue/ugc/profile/?user_id={}&media_id={}&request_source=1'.format(user_id,media_id)
            }
            r2 = requests.get(url, headers = headers)
            print(r2.text)
            js = json.loads(r2.text)
            offset = js['offset']
            datas = js['data']
            for data in datas:
                try:
                    content = json.loads(data['content'])
                    if 'raw_data' not in content or content['raw_data'] == None:
                        if 'rich_content' in content:
                            title = content['rich_content']
                        else:
                            title = content['title']
                        id = content['rid']
                        comment = content['comment_count']
                        digg = content['digg_count']
                        forward = content['forward_info']['forward_count']
                        try:
                            publish_time = content['publish_time']
                        except:
                            publish_time = content['create_time']
                    else:
                        id = content['rid']
                        raw_data = content['raw_data']
                        title = raw_data['title']
                        action = raw_data['action']
                        comment = action['comment_count']
                        digg = action['digg_count']
                        forward = action['forward_count']
                        publish_time = raw_data['create_time']
                    print(title.translate(dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd))[:25])
                    publish_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(publish_time))
                    f_csv.writerow([name,publish_count,following,fans,all_digg,verified,description,
                                    id,title,publish_time,comment,forward,digg])
                except:
                    print('error')
                    continue
            print(offset)
            times -= 1
