import requests
import json
import importlib
import sys
import os
import re
import time

def readHotel():
    importlib.reload(sys)
    plates = ["sh"]#["sz","sh"]
    column = {"sz":"szse","sh":"sse"}
    for pla in plates:
        for year in range(2007,2020):
            for page in range(1,1000):
                path = "E:/python项目/巨潮_社会责任报告/pdf/"+pla
                begin = len([lists for lists in os.listdir(path) if os.path.isfile(os.path.join(path, lists))])
                print(str(pla)+str(year)+" "+str(page)+" begin")
                headers = {"Accept": "application/json, text/javascript, */*; q=0.01",
                            "Accept-Encoding": "gzip, deflate",
                            "Accept-Language": "zh-CN,zh;q=0.9",
                            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
                           "Cookie":"noticeTabClicks=%7B%22szse%22%3A3%2C%22sse%22%3A1%2C%22hot%22%3A0%2C%22myNotice%22%3A1%7D; tradeTabClicks=%7B%22financing%20%22%3A0%2C%22restricted%20%22%3A0%2C%22blocktrade%22%3A0%2C%22myMarket%22%3A0%2C%22financing%22%3A1%7D; JSESSIONID=781503D7473C24B3891562A4B572D3C3; cninfo_search_record_cookie=%E7%A4%BE%E4%BC%9A%E8%B4%A3%E4%BB%BB%E6%8A%A5%E5%91%8A; _sp_id.2141=903ca2fe-aa95-43c2-a6a8-de4696b11048.1563280311.1.1563280959.1563280311.77c74db5-ccf9-4f8e-b49e-bbfd405f54d6; UC-JSESSIONID=B8989CDFFAD61605BEBF3455C5801C9D",
                           "Host": "www.cninfo.com.cn",
                            "Origin": "http://www.cninfo.com.cn",
                            "Referer": "http://www.cninfo.com.cn/new/commonUrl?url=disclosure/list/notice",
                            "X-Requested-With": "XMLHttpRequest",
                           }
                url="http://www.cninfo.com.cn/new/hisAnnouncement/query"
                payload={
                    "pageNum": str(page),
                    "pageSize": "30",
                    "tabName": "fulltext",
                    "column": column[pla],
                    "stock":"" ,
                    "searchkey": "社会责任报告",
                    "secid":"" ,
                    "plate": pla,
                    "category": "",
                    "trade":"" ,
                    "seDate": str(year) + "-01-01+~+" + str(year) +"-12-31"#"2017-01-01+~+2017-12-31"
                    }
                req = requests.post(url,headers = headers, params=payload)
                # 转化为JSON对象
                content = json.loads(req.text)
                print(len(content["announcements"]))
                if ifEnd(content):
                    break
                downLoad(content, pla, year-1, page)
                time.sleep(2)
                end = len([lists for lists in os.listdir(path) if os.path.isfile(os.path.join(path, lists))])
                print(end - begin)
                if end-begin!= len(content["announcements"]):
                    print("####################")
                    downLoad(content, pla, year-1, page)
                if end-begin!= len(content["announcements"]):
                    print("####################")
                    downLoad(content, pla, year-1, page)
                end = len([lists for lists in os.listdir(path) if os.path.isfile(os.path.join(path, lists))])
                print(end - begin)
                
def ifEnd(content):
    if len(content["announcements"]):
        return False
    else:
        return True

def downLoad(content, pla, time, page):
    for businese in content["announcements"]:
        downloadUrl = businese["adjunctUrl"]
        title = businese["announcementTitle"].replace("/","-")
        code = businese["secCode"]
        res = requests.get("http://static.cninfo.com.cn/"+businese["adjunctUrl"])
        filePath = "E:\\python项目\\巨潮_社会责任报告\\pdf\\"+pla+"\\"+code+"+" + str(time) + "+" + title + ".pdf"
        if not os.path.exists(filePath):
            with open(filePath, 'wb') as f:
                f.write(res.content)
readHotel()
