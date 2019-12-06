import requests
from pymongo import MongoClient
import json
from urllib.parse import quote

searchKey = '碧悠'
dbName = '碧悠'
myclient = MongoClient("mongodb://localhost:27017/")
mydb = myclient["ZhiHu"]
mycol = mydb[dbName]
newcol = mydb[dbName+'-问题']
idList = []
for x in mycol.find():
    if x['type'] == 'answer':
        if searchKey in x['question']['name'] :
            if x['question']['id'] not in idList:
                idList.append(x['question']['id'])
        else:
            if searchKey not in x['content']:
                mycol.delete_one(x)
for id in idList:
    offset = 0
    while True:
        url = 'https://www.zhihu.com/api/v4/questions/{}/answers?&limit=10&offset={}&include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_labeled%2Cis_recognized%2Cpaid_info%2Cpaid_info_content%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%2A%5D.topics'.format(id,offset)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        }
        print(url[:100])
        r = requests.get(url,headers=headers)
        js = json.loads(r.text)
        if len(js['data']) == 0:
            break
        for data in js['data']:
            newcol.insert_one(data)
        offset += 10


# 知乎搜索页爬虫
def search_zhihu_by_searchKey():
    conn=MongoClient('127.0.0.1', 27017)
    db= conn.ZhiHu
    searchKey = '光明如实'
    offset = 0
    while True:
        url = 'https://www.zhihu.com/api/v4/search_v3?t=general&q={}&correction=1&offset={}&limit=20&show_all_topics=0'.format(searchKey,offset)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        }
        print(url)
        r = requests.get(url,headers=headers)
        js = json.loads(r.text)
        if len(js['data']) == 0:
            break
        resultList = js['data']
        for result in resultList:
            if result['type'] == 'search_result':
                db[searchKey].insert_one(result['object'])
        offset += 20
    return
#search_zhihu_by_searchKey()
