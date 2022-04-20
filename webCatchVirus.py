import pandas as pd
import re
import requests
from bs4 import BeautifulSoup
from Naviresult import transGeo
from datetimechange import dTransformEtoC
from DBconn import writedata
from foliumgeolayer import drawchart
from cleanNavidata import cleanNavi
import datetime

global headers
headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 7_1_2 like Mac OS X) AppleWebKit/537.51.2 (KHTML, like Gecko) Version/7.0 Mobile/11D257 Safari/9537.53',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
           'Connection': 'keep-alive', 'Accept-Language': 'zh-CN,zh;q=0.9,en-CN;q=0.8,en;q=0.7', 'Accept-Encoding': 'gzip, deflate, br'} # 表头很重要，否则真的会报错

def getLink():
    url = 'https://ss.shanghai.gov.cn/service/wsjkw/search?&dateOrder=2' # "?&dateOrder=2" 用来解决第一页搜不到最新日期，加上这个可以安日期排序
    key = '本市各区确诊病例、无症状感染者居住地信息'
    params = {'siteId': 'all', 'siteArea': 'all', 'q': key, 'all': 1}
    result=requests.get(url, headers=headers, params=params)
    result.encoding='utf-8'
    soup=BeautifulSoup(result.text, 'lxml')
    #print(soup)
    title=[]
    link=[]
    for x in soup.find_all (class_='result'):
        if '本市各区确诊病例、无症状感染者居住地信息' in x.find('a').get('title'):
            title.append(x.find('a').get('title'))
            link.append(x.find(class_='url').find('a').get('href'))
    result=pd.DataFrame()
    result['title'] = title
    result['link'] = link
    result['date'] = result['title'].str.split('（', expand=True)[0]
    print(result['date'])
    return result

def getAdd():
    clean_result = pd.DataFrame()
    address = []
    result = getLink()
    ercode = 0
    for y in range(len(result['date'])):
        if 'weixin.qq.com' not in result.iloc[y]['link']:
            ercode = 405
            continue
        else:
            a = dTransformEtoC()
            if a in result.iloc[y]['date']:
                ercode = 888
                req = requests.get(result.iloc[y]['link'], headers=headers)  # 在一个表里用iloc定位 link列的第一行，必须用iloc 定位！
                req.encoding = 'utf-8'
                soup = BeautifulSoup(req.text, 'lxml')
                # print(soup)
                cleanaddress = pd.DataFrame()
                for x in soup.find(class_='rich_media_content').find_all('p'):
                    regex_str = '[\u4E00-\u9FA5]*[0-9]*[\u4E00-\u9FA5]，'
                    if (re.match(regex_str, x.text)):
                        address.append(x.text.strip('，'))
                    regex_str = '[\u4E00-\u9FA5]*[0-9]*[\u4E00-\u9FA5]。'
                    if (re.match(regex_str, x.text)) and "已对相关居住地" not in x.text:
                        address.append(x.text.strip('。'))
                cleanaddress['address'] = address
                cleanaddress['date'] = result.iloc[y]['date']
                cleanaddress['address'] = '上海'+cleanaddress['address']
                cleanaddress['json'] = cleanaddress['address'].apply(lambda x: transGeo(x))
                clean_result = pd.concat([clean_result, cleanaddress])  # 第一次用pd.concat,取代append
                fName = 'Temp%s.csv' % a
                clean_result.to_csv(fName)
                cleanN = cleanNavi(fName)
                writedata(cleanN) #写入数据库
            continue
    print(ercode)
    print(clean_result)

if __name__ == '__main__':
    getLink()
    getAdd()
    duration = 4
    drawchart(duration)
    print(datetime.date, 'is well loaded')









