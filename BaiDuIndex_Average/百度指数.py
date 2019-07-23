import requests
import json
from urllib.parse import quote
import string
import csv
'''
#payload={"word":"环保","area":0,"days":30}
word = "环保"
url_search="http://index.baidu.com/api/SearchApi/index?area=0&word="+word+"&startDate=2017-01-01&endDate=2017-12-31"
url_media = "http://index.baidu.com/api/NewsApi/getNewsIndex?area=0&word="+word+"&startDate=2017-01-01&endDate=2017-12-31"
url = quote(url,safe=string.printable)
r=requests.get(url,headers=headers)
js = json.loads(r.text)
avg = js["data"]["generalRatio"][0]["all"]["avg"]
print(avg)
'''
def count_avg_search(word):
    print(word)
    for year in range(2011,2018):
        try:
            url = "http://index.baidu.com/api/NewsApi/getNewsIndex?area=0&word="+word+"&startDate="+str(year)+"-01-01&endDate="+str(year)+"-12-31"
            url = quote(url,safe=string.printable)
            r=requests.get(url,headers=headers)
            js = json.loads(r.text)
            #avg = js["data"]["generalRatio"][0]["all"]["avg"]
            avg = js["data"]["index"][0]["generalRatio"]["avg"]
            count[word][str(year)] = avg
        except:
            print("error")

def input_csv(count):
    with open('e.csv','a',newline='') as csvfile:
        csv_write=csv.writer(csvfile)
        csv_write.writerow(["词语","2017","2016","2015","2014","2013","2012","2011"])
        for word in count:
            csv_write.writerow([word,count[word]["2017"],count[word]["2016"],count[word]["2015"],count[word]["2014"],count[word]["2013"],count[word]["2012"],count[word]["2011"]])
    

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
           "x-requested-with":"XMLHttpRequest",
           "Cookie":"BIDUPSID=8568727978FE7DDE3328D369EE20F5BD; PSTM=1508561167; BAIDUID=83B8AB7EEFE6159FCE9CBB85EBA6BA20:FG=1; BDUSS=GljV3ZnbFBDSkhSenpyUzV4eTFGNjhTT2x2WDd6WVJ3S2c1S0dLRG1yQlJkS2hiQVFBQUFBJCQAAAAAAAAAAAEAAABA8rZPRGFtb25keW0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFHngFtR54BbV; bdshare_firstime=1539246308899; Hm_lvt_ba7c84ce230944c13900faeba642b2b4=1539684768,1539962728; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; delPer=0; PSINO=7; BDSFRCVID=mtIsJeCCxG37sLJ7nqZloAB3b8FOeQZRddMu3J; H_BDCLCKID_SF=tR30WJbHMTrDHJTg5DTjhPrMhqOAbMT-027OKK85-hRkMnrlW4voLfjy-G7lW-QIyHrb0p6athF0HPonHjKMejJb3J; Hm_lvt_d101ea4d2a5c67dab98251f0b5de24dc=1542335400,1542641155,1542711573,1542812131; bdindexid=trub0fqk3h9h3eiu469in01oj6; Hm_lpvt_d101ea4d2a5c67dab98251f0b5de24dc=1542812359; ZD_ENTRY=baidu; H_PS_PSSID=1450_21086_18559_20691_27376_20718"
            }
word_list_pub = ["水污染","大气污染","土壤污染","噪声污染","核污染","光污染","白色污染","海洋污染","臭氧层","沙漠化","温室效应","酸雨","pm2.5","绿色产品","绿色交通","节能","减排","低碳","清洁能源","回收","以旧换新","一次性","绿色食品","生态旅游"]
word_list_gov = ["绿色发展","绿色产业","绿色经济","生态文明建设","绿色GDP","可持续发展","环保法","人与自然和谐发展","绿色农业","绿色科技","五位一体","绿色金融","循环经济","节约资源","保护环境","低碳经济"]
count = {}
word_list = word_list_pub + word_list_gov
for word in word_list:
    count[word] = {"2011":0,"2012":0,"2013":0,"2014":0,"2015":0,"2016":0,"2017":0}
    count_avg_search(word)
input_csv(count)
