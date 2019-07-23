from selenium import webdriver
import time
import os
#环境要求：python3、chrome浏览器、chromedriver（同一文件夹中）
#文件夹要求：需先新建d:/data负责存储推送内容，或修改代码中的写入文件夹

#计时开始
start=time.clock()
#浏览器头和初始地址设置
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}
url = "https://weixin.sogou.com"
#初始化selenium的载体chrome浏览器
chromeOptions = webdriver.ChromeOptions()
#chromeOptions.add_experimental_option()
browser = webdriver.Chrome(chrome_options=chromeOptions)
################################################################################正式处理部分
############################################################访问搜狗微信主页
browser.get(url)
#查找搜索栏并输入关键词
input = browser.find_element_by_id("query")
input.send_keys("中山大学附属中学")
#点击搜索
button = browser.find_element_by_class_name("swz2")
button.click()
#降低访问速度
time.sleep(1)
############################################################点击，进入公众号主页
target = browser.find_element_by_link_text("中山大学附属中学")
target.click()
#切换目标标签至新标签处
browser.switch_to_window(browser.window_handles[1])
#获得最近推送数组
message = browser.find_elements_by_class_name("weui_media_title")
#有时会出现网络延迟以致获取不了，等待，已确保获取
while not len(message):
    time.sleep(1)
    message = browser.find_elements_by_class_name("weui_media_title")
#遍历推送数组
for i in range(len(message)):
    #####################################################################进入推送
    newMessage = browser.find_elements_by_class_name("weui_media_title")
    newMessage[i].click()
    #获得标题和内容
    content = browser.find_element_by_class_name("rich_media_content ")
    title = browser.find_element_by_class_name("rich_media_title")
    #输出。注意！！！！！必须先在d盘创建data文件夹（或修改为其他文件夹）
    with open('D:/data/'+title.text+'.txt', 'w',encoding='utf-8') as f:
        f.write(content.text)
    #返回上一页
    browser.back()
    time.sleep(1)
end = time.clock()
#显示使用时间
print("time :" + str(end-start))