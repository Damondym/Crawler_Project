import requests
from bs4 import BeautifulSoup
import re
from collections import Counter
import sys
import csv
import random
import time
import datetime
import json
import os

def get_shop_main(url):
    r = requests.get(url,headers=headers)
    soup = BeautifulSoup(r.text,'html.parser')
    name = soup.find('h1',{'class':'shop-name'}).get_text()
    reviewNum = soup.find('span',{'class':'reviews'}).get_text().replace('条评论','')
    price = re.findall('人均：(\S+)元',soup.find('span',{'class':'price'}).get_text())[0]
    scoreList = soup.find('span',{'class':'score'}).find_all('span')
    kouwei = scoreList[0].get_text()[3:]
    huanjing = scoreList[1].get_text()[3:]
    fuwu = scoreList[2].get_text()[3:]
    return

def get_shop_comment(url,writer,name=''):
    page = 0
    while url:
        page += 1
        #if page > 80:
        #    break
        print('#####################################'+name+url[-5:])
        while True:
            try:
                r = requests.get(url,headers = headers)
                soup = BeautifulSoup(r.text,'html.parser')
                name = soup.find('h1',{'class':'shop-name'}).get_text()
                reviewList = soup.find('div',{'class':'reviews-items'}).find('ul').find_all('div',{'class':'main-review'})
                #下面这个正则的网址经常会被修改！！！但是目前只能遇到错误了再人为修改
                css_link = re.findall(r'<link rel="stylesheet" type="text/css" href="//s3plus.sankuai.com/v1/(.*?)">', r.text)
                css_link_all = 'http://s3plus.sankuai.com/v1/' + css_link[0]
                break
            except Exception as e:
                print(url)
                print(repr(e))
                print(r.text)
                time.sleep(random.randint(1,3))
        print(css_link[0])
        if os.path.exists(css_link[0][-10:] + '.txt'):
            with open(css_link[0][-10:] + '.txt','r')as f1:
                font_dict = json.loads(f1.read())
        else:
            font_dict = get_font_dict(css_link_all)
            with open(css_link[0][-10:] + '.txt','w+')as f1:
                f1.write(json.dumps(font_dict))
        for review in reviewList:
            user = review.find('a',{'class':'name'}).get_text().strip()
            print(user)
            level = re.findall('squarelv(\d+).png',soup.find('img',{'class':'user-rank-rst'})['src'])[0]
            if soup.find('span',{'class':'vip'}):
                vip = 1
            else:
                vip = 0
            rank = review.find('div',{'class':'review-rank'})
            total = re.findall('sml-str(\d+)',str(rank))[0]
            score = rank.find_all('span',{'class':'item'})
            if len(score):
                kouwei = score[0].get_text().strip()[3:]
                huanjing = score[1].get_text().strip()[3:]
                fuwu = score[2].get_text().strip()[3:]
            else:
                kouwei = ''
                huanjing = ''
                fuwu = ''
            commentTime = review.find('span',{'class':'time'}).get_text().strip()
            action = re.sub('[\s\n]+','',review.find('span',{'class':'actions'}).get_text())
            like = re.findall('赞[\(]{0,1}([\d]*)',action)[0]
            reply = re.findall('回应[\(]{0,1}([\d]*)',action)[0]
            recommend = review.find('div',{'class':'review-recommend'})
            recommendList = ''
            if recommend:
                recommend = recommend.find_all('a',{'class':'col-exp'})
                for food in recommend:
                    recommendList += food.get_text() + ','
            else:
                recommendList = ''
            
            # 评论内容
            content = review.find('div',{'class':'review-words'})
            if content:
                content = get_comment_page(content,font_dict)
            else:
                content = get_comment_page(review.find('div',{'class':'review-words Hide'}),font_dict)
                content = content.replace('收起评论','')
            writer.writerow([name,url,user,level,vip,commentTime,total,kouwei,huanjing,fuwu,
                             content,like,reply,recommendList])
        try:
            url = 'http://www.dianping.com' + soup.find('a',{'class':'NextPage'})['href']
        except:
            print('######end')
            break
        time.sleep(random.randint(1,3))

def get_comment_page(html,font_dict):  # 获得评论内容
    class_set = set()
    for span in re.findall(r'<svgmtsi class="([a-zA-Z0-9]{5,6})"></svgmtsi>', str(html)):
        class_set.add(span)
    for class_name in class_set:
        try:
            html = re.sub('<svgmtsi class="%s"></svgmtsi>' % class_name, font_dict[class_name], str(html))
        except:
            print('########'+class_name)
    non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
    try:
        return re.sub('[\s]+',' ',BeautifulSoup(html.translate(non_bmp_map),'html.parser').get_text())
    except:
        return html.get_text()
def get_font_dict_by_offset(url):
    """
        获取坐标偏移的文字字典, 会有最少两种形式的svg文件（目前只遇到两种）
    """
    print('background'+url)
    start_y = 23
    font_size = 14
    res = requests.get(url,timeout=60)
    html = res.text
    font_dict = {}
    y_list = re.findall(r'd="M0 (\d+?) ', html)
    if y_list:
        font_list = re.findall(r'<textPath .*?>(.*?)<', html)
        for i, string in enumerate(font_list):
            y_offset = start_y - int(y_list[i])

            sub_font_dict = {}
            for j, font in enumerate(string):
                x_offset = -j * font_size
                sub_font_dict[x_offset] = font

            font_dict[y_offset] = sub_font_dict
    else:
        font_list = re.findall(r'<text.*?y="(.*?)">(.*?)<', html)

        for y, string in font_list:
            y_offset = start_y - int(y)
            sub_font_dict = {}
            for j, font in enumerate(string):
                x_offset = -j * font_size
                sub_font_dict[x_offset] = font

            font_dict[y_offset] = sub_font_dict
    return font_dict

def get_font_dict(url):
    """
        获取css样式对应文字的字典
    """
    res = requests.get(url, headers=headers)
    html = res.text
    background_image_link = re.findall(r'background-image: url\((.*?)\);', html)
    assert background_image_link
    #以下同样为随时变化的值！！！！！！
    backid = 1
    while True:
        try:
            background_image_link = 'http:' + background_image_link[backid]
            html = re.sub(r'span.*?\}', '', html)
            group_offset_list = re.findall(r'\.([a-zA-Z0-9]{5,6}).*?round:(.*?)px (.*?)px;', html)  # css中的类
            font_dict_by_offset = get_font_dict_by_offset(background_image_link)  # svg得到这里面对应成字典
            font_dict = {}
            for class_name, x_offset, y_offset in group_offset_list:
                y_offset = y_offset.replace('.0', '')
                x_offset = x_offset.replace('.0', '')
                # print(y_offset,x_offset)
                if font_dict_by_offset.get(int(y_offset)):
                    font_dict[class_name] = font_dict_by_offset[int(y_offset)][int(x_offset)]
            break
        except:
            print(background_image_link)
            backid += 1
    return font_dict

def get_ip():
    url = 'http://www.89ip.cn/tqdl.html?api=1&num=1000&port=&address=&isp='
    r = requests.get(url)
    ip = re.findall('([\d\.\:]+)<br>?',r.text)
    return ip


canteenUrl = 'http://www.dianping.com/shop/92149656/review_all'
headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',   
        'Cookie': '_lxsdk_cuid=16662acc2dec8-079acf4d80b782-333b5602-1fa400-16662acc2dfc8; _lxsdk=16662acc2dec8-079acf4d80b782-333b5602-1fa400-16662acc2dfc8; cy=4; cye=guangzhou; _hc.v=e6a81fa2-34e8-30df-e4e1-bce316165889.1576806828; _dp.ac.v=d0e06310-d02a-4203-9ba6-8affab00b71b; ua=15013216710; s_ViewType=10; cityid=4; default_ab=shop%3AA%3A5; ctu=7926b9869ae6b89b8e06e031a2e402762c8e97d446f37d239335cb1e8d901485; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; dper=f912b5c4be8182a0e7edcbbb1487725f58824ff12efc2fb899bc7e4fd892fbe9fbccc23d0d783757df7194c68c72558d856deaa8cbf73790aba11c28aa9ee635f5fd117efc65e0773fe634f30151ca96f577f06d687a2107e4ef4c076c16fa1d; ll=7fd06e815b796be3df069dec7836c3df; _lxsdk_s=16f3fe5e84d-86c-e80-d6e%7C%7C1042'
        }
with open('e.csv','w',newline='',encoding = 'utf-8-sig')as f:
    f_csv = csv.writer(f)
    header = ['餐厅名','评论url','用户名','用户等级','是否VIP','评论时间','综合评分','口味','环境','服务',
              '评论内容','点赞数','回应数','推荐菜','','','','','']
    f_csv.writerow(header)
    get_shop_comment(canteenUrl,f_csv)
    '''
    key = ''
    url = 'http://www.dianping.com/search/keyword/4/0_{}/o3'.format(key)
    while True:
        print('######################' + url[-5:])
        r = requests.get(url,headers = headers)
        soup = BeautifulSoup(r.text,'html.parser')
        idList = soup.find_all('a',{'data-click-name':'shop_title_click'})
        for id in idList:
            print('##########################' + id['title'])
            shopid = id['data-shopid']
            newUrl = 'http://www.dianping.com/shop/{}/review_all'.format(shopid)
            get_shop_comment(newUrl,f_csv,id['title'])
        url = soup.find('a',{'class':'next'})['href']
    '''
'''
r = requests.get(url,headers=headers)
rl = re.findall('.z[a-zA-Z0-9]{4,5}.*?round:.*?px -(.*?)px;',r.text)
r1 = [float(i) for i in rl]
print(len(rl))
r1.sort()
r2 = {}
for i in set(rl):
    r2[i] = rl.count(i)
print(r2)
'''

