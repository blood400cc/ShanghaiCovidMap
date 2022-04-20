
import folium
import webbrowser as wb
from DBconn import readdata
from datetime import datetime, timedelta
import geopandas as gpd
from folium.plugins import Search

def getDBdata(duration):
    date = []
    for i in range(0,duration):
        a = i+1 #主要是控制到底能读取前几天的数
        b = datetime.today() + timedelta(-a)
        date.append(str(b.date())) # 空表如果直接按index位添加元素会报错，必须append
    sql = "select * from virusgeo where Date>='%s'" % date[(duration-1)] # 必须要减1，因为range的尾巴数字是开口不算的
    cdata = readdata(sql)
    data = cdata.drop(columns=['City', 'District'])
    gdf = gpd.GeoDataFrame(data, geometry=gpd.points_from_xy(data.Longitude, data.Latitude), crs="epsg:4326")  # 为了这一句啊，费了半天的劲，这是实现搜索框的关键啊！
    #gdf['location'] = gdf['Latitude'].map(str)+','+gdf['Longitude'].map(str) # 尝试压缩成经纬度的location直接让circlemarker读取，但不行，那个只能每次读一个点。非要用循环； 另外这里有个知识困惑点，df.location 与df['location']好像是等价的，没听说过啊
    return date, gdf

def geomarkers(cdata,shmap,date,color,i):
    data = cdata[cdata['Date']==date[i]]
    folium.GeoJson(data,
                   name=date[i], control=True, overlay=True,
                   marker=folium.CircleMarker(radius=1, color=color[i], fill=True, fill_color=color[i], fill_opacity=1),
                                              tooltip=folium.GeoJsonTooltip(fields=["Address", "Date"], aliases=['地址：', '发现日期：']
                                                                              )).add_to(shmap)

def drawchart(duration):
    longitude = 121.568585
    latitude = 31.252882
    amap = 'http://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x={x}&y={y}&z={z}'
    shmap = folium.Map(location=[latitude, longitude], zoom_start=12, name='Virusmap', tiles=None, aliases=['疫情日期选择'],  attr='default')
    tile_layer = folium.TileLayer(
        tiles = amap,
        attr='default',
        name ='疫情时间选择',
        control=False,
        opacity=1
        ).add_to(shmap)
    date, cdata = getDBdata(duration)
    gdata = cdata.drop(columns=['Latitude','Longitude'])
    color = ["#ff6666", "#a3cca3", "#FF99CC", "#CCCCFF", "#99ccff", "#666699", "#ea80b0", "#ffcc33"]
    for i in range(0,duration):
        geomarkers(gdata,shmap,date,color,i) # method markers() 需要先定义再引用，否则会不认识
    citygeo = folium.GeoJson(gdata,
                             name='baseDate', control=True, overlay=True, show=False,
                             marker=folium.CircleMarker(radius=0.1, weight=0, fill_color='white'
                                                        )).add_to(shmap)
    Search(layer=citygeo, placeholder='街道村镇搜索', search_label="Address").add_to(shmap)
    folium.LayerControl('topleft').add_to(shmap)
    #shmap.save('out1.html')
    #wb.open('out1.html')
    shmap.save('//MKNAS/Nginx/html/catchvirus.html')

if __name__ == '__main__':
    duration = 3
    drawchart(duration)
