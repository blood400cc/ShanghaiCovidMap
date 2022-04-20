import pandas as pd
from datetime import datetime
from DBconn import writedata

def cleanMonth(datetemp): # 解决 4月前面有【最新】这种问题
    j = 0
    for a in datetemp:
        j += 1
        if a == '月':
            j = j - 2
            break
    date = datetemp[j:]
    return date

def cleanNavi(fName):
    reader = pd.read_csv(fName, sep=',', encoding='utf-8')
    #print(reader.info)
    coords = pd.DataFrame()
    locD = []
    locC = []
    cosJ = []
    cosW = []
    date = []
    address = []
    for i in range(0, len(reader)):
        result = eval(reader.iloc[i]['json'])  # json.loads()理论上也可以，但需要严格的双引号，这里都是单引号
        if 'DATA_ERROR' not in result['info']:
            datetemp1 = reader.iloc[i]['date']
            datetemp2 = cleanMonth(datetemp1)
            dt_time = datetime.strptime(datetemp2, '%m月%d日').date().replace(year=2022) #这里是很巧妙的一个转换原有的“4月5日”这种格式回成标准的日期格式，因为没用年还加了个replace, 正常应该是'%Y年%m月%d日'
            date.append(dt_time)
            addresstemp = reader.iloc[i]['address']
            address.append(addresstemp)
            temp = result['geocodes'][0]['location'].split(",") # 太巧妙了，就是用了简单的【0】，相当于切了list的第一个元素，而geocodes后面的列表里，就只有这一个dict作为大元素！于是就切出list来了 / str.split("分隔符") 可以将字符串按分隔符直接拆成列表
            jDegree = temp[0]
            wDegree = temp[1]
            district = result['geocodes'][0]['district']
            city = result['geocodes'][0]['city']
            cosJ.append(jDegree)  #而且这个地方不能用 cos = cos.append(xxx), 只能用直接 cos.append()
            cosW.append(wDegree)
            locD.append(district)
            locC.append(city)
        else:
            continue
        #print(cos)
    coords['Address'] = address
    coords['Date'] = date
    coords['City'] = locC
    coords['District'] = locD
    coords['Longitude'] = cosJ
    coords['Latitude'] = cosW
    #print(coords)
    cleanN = coords[coords['District'].str.contains('区', na=False)] # 为了去除某个数据段包含的[] 导致sql报错，na=False的意思就是，遇到非字符串的情况，直接忽略。更熟悉PD的筛选方法了，你也可以写na=True，意思就是遇到非字符串的情况，计为筛选有效
    return cleanN



if __name__ == '__main__':
    fName = 'Temp4月12日.csv'
    tempN = cleanNavi(fName)
    print(tempN)
    writedata(tempN)  # 写入数据库

