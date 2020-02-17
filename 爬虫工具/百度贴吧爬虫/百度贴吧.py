import requests
from bs4 import BeautifulSoup
import re
import csv
import time

searchKey = '国双'
with open('e.csv','w',newline='',encoding = 'utf-8-sig')as f:
    f_csv = csv.writer(f)
    header = ['标题','内容','时间','url']
    f_csv.writerow(header)
    url = 'http://tieba.baidu.com/f/search/res?isnew=1&kw=&qw={}&rn=20&pn=1'.format(searchKey)
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
        }
    while True:
        print('###########################################new page '+url[-6:])
        r = requests.get(url,headers = headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        try:
            postList = soup.find('div',{'class':'s_post_list'}).find_all('div',{'class':'s_post'})
        except:
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!search fail")
            print(url[-6:])
        print(len(postList))
        for post in postList:
            try:
                title = post.find('span',{'class':'p_title'}).get_text()
                href = post.find('span',{'class':'p_title'}).a['href']
                create_time = post.find('font',{'class':'p_green p_date'}).get_text()
                cid = re.findall('cid=\d*#(\d*)',href)[0]
                content = post.find('div',{'class':'p_content'}).get_text()
            except Exception as e:
                print('!!!!!!!!!!!!!!!!!!!!!!post fail')
                print(href)
                print(repr(e))
            # 具体文章的爬取
            tiebaUrl = 'http://tieba.baidu.com'+href
            headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
            }
            try:
                tiebaRes = requests.get(tiebaUrl,headers = headers)
                tiebaSoup = BeautifulSoup(tiebaRes.text, 'html.parser')
                content = tiebaSoup.find('div',{'id':'post_content_'+cid}).get_text()
            except Exception as e:
                print('!!!!!!!!!!tieba fail')
                print(href)
                print(repr(e))
            f_csv.writerow([title,content,create_time,tiebaUrl])
        try:
            url = 'http://tieba.baidu.com' + soup.find('a',{'class':'next'})['href']
            time.sleep(3)
        except:
            print('!!!!!!!!!!!!!!!!!!!!!!!!page end')
            print(url)
            break
