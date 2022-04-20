import requests
import json
from retrying import retry

@retry(stop_max_attempt_number=3) # 因为老断线，只好加个retry的修饰函数，并且timeout从2修改到了30，还是管用的，运行18个小时再也没断过
def transGeo(geo):
    with open('amapkey.txt', 'r') as f:
        amapkey = f.read()
    parameters = {'address': geo, 'key': amapkey}
    base = 'https://restapi.amap.com/v3/geocode/geo'
    loc=0
    result = requests.get(base, parameters, timeout=30)
    answer = result.json()
    return answer



