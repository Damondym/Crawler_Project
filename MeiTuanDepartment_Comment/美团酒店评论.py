import requests
import json
import importlib
import sys

def readHotel():
    importlib.reload(sys)
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
    #一页页遍历
    for page in range(32):#页码+1，url中的limit表示返回的酒店数，offset就是目前已经返回的酒店数。一次返回的酒店数不能超过50个，所以干脆一页页返回
        url="https://ihotel.meituan.com/hbsearch/HotelSearch?utm_medium=pc&version_name=999.9&cateId=20&attr_28=129&uuid=57A70FB3E15582C984BABB36D496C9883EB98CC6CF47D2F4844E595FC30A6E93%401532792217452&cityId=287&offset="+str((page-1)*20)+"&limit=20&startDay=20181231&endDay=20181231&q=&sort=defaults&X-FOR-WITH=V6FgB9PK3EDPMzopNr5CcJbDtxmoedET1xr1CUozjVe%2Bshng3QsvaHgRnhDcsBeXQa%2F109loEGsoxXmpF8qYL9MYq9X8JIaoGdgYVMzp7nJA%2BIsv%2FO6k6hUKuZQUvu%2BuRMb9pCBy7YvPkX6hRlnKjg%3D%3D"
        # 访问网页
        req = requests.get(url,headers = headers)
        # 获取内容
        charset = req.encoding
        content = req.text.encode(charset).decode('utf-8')
        # 转化为JSON对象
        json_con = json.loads(content)
        # 获取酒店列表
        hotel_list = json_con['data']['searchresult']

        # 获取具体内容
        for hotel in hotel_list:
            hotelId = hotel['poiid']
            #每个酒店获取对应评论
            readComment(hotelId)

def readComment(id):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
    #url中的limit和上面作用一样，但是由于这次返回次数没有限制，所以直接设置返回1000，如果需要更多可以继续设大一点，也可以动态爬取页面评论数来设置（不过感觉有点多余了），如果酒店没有这么多评论会自动停止的。
    url="http://ihotel.meituan.com/group/v1/poi/comment/"+str(id)+"?sortType=default&noempty=0&withpic=0&filter=all&limit=1000&offset=0&X-FOR-WITH=5I2vBz2LdLTvG5ZTemwwA%2FSxcOEzpjns9aAu8fDtZDT6Z2Mpu5kwZ8eash1hEbC4eAGT9%2BqTkAZor7KtyTe4mpKj3Wf6GpfpLLBSeKS0T0gXR%2F9JTaA7cD6DkAUFIK%2B7ObPfgnXtHRPm9%2FqjYuxunw%3D%3D"
    # 访问网页
    req = requests.get(url,headers = headers)
    # 获取内容
    charset = req.encoding
    content = req.text.encode(charset).decode('utf-8')
    # 转化为JSON对象
    json_con = json.loads(content)
    # 获取评论列表
    comment_list = json_con['data']['feedback']
    print("开始爬取  "+str(id)+"  评论")
    # 获取具体内容
    for comment in comment_list:
        content = comment['comment']
        #设置try主要是因为评论当中如果有表情的的话就转化不了，所以干脆把表情的（非常少数）过滤掉
        try:
            #打印评论
            print(content)
        except:
            continue

readHotel()
