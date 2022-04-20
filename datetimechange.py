from datetime import datetime, timedelta

def dTransformEtoC():
    now = datetime.today() + timedelta(-1)
    nowC = now.strftime("%Y年%#m月%d日")
    if nowC[-3] == '0':
        a = nowC.replace('月0', '月') #去掉日期前的0，将4月07日变成4月7日
        c = a[5:]
    else:
        c = nowC[5:] # 针对双位数日期还是要还原
    c = c.lstrip('0') # linux系统的日期月份前会有个0，必须用这个语句再处理一下
    print(c)
    return c

if __name__ == '__main__':
    dTransformEtoC()
