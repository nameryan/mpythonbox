from mpython import*
import json
import urequests                    #用于网络访问的模块
from machine import Timer           #定时器模块
import ntptime,network              # 导入国际标准时间、网络模块
import music
import neopixel

API_KEY = 'SboqGMxP4tYNXUN8f'                 #心知天气API密钥（key）

url_now="https://api.seniverse.com/v3/weather/now.json"           #获取天气实况的请求地址
url_daily="https://api.seniverse.com/v3/weather/daily.json"       #获取多日天气预报的请求地址

oled.DispChar('联网中...',40,25)     #OLED屏显示联网提示
oled.show()

mywifi=wifi()
mywifi.connectWiFi("SynologySmartConnect","=ge1412ro")          #连接 WiFi 网络

my_rgb = neopixel.NeoPixel(Pin(Pin.P13), n=4, bpp=3, timing=1)

ntptime.settime(8, "ntp.ntsc.ac.cn")                    #授时

my_rgb.fill( (0, 0, 0) )
my_rgb.write()                                           #RGB灯

_event_changed_10 = False

tim10 = Timer(10)

def timer10_tick(_):                                   #设置整点报时
    global _event_changed_10
    if (time.localtime()[4] == 0):
        if not _event_changed_10: _event_changed_10 = True; on_custom_event_10()
    else: _event_changed_10 = False

def on_custom_event_10():
    global time_s1
    music.play('C3:1')
    time.sleep_ms(50)
    music.play('C3:1')
    time.sleep_ms(50)




_event_changed_8 = False

tim8 = Timer(8)

#year includes the century (for example 2014).
#month is 1-12
#mday is 1-31
#hour is 0-23
#minute is 0-59
#second is 0-59
#weekday is 0-6 for Mon-Sun
#yearday is 1-366

def timer8_tick(_):                           #设置闹钟提醒
    global _event_changed_8
    #every 6:50 on weekday 
    if (time.localtime()[3] == 6 and time.localtime()[4] == 50 and time.localtime()[6] < 5):
        if not _event_changed_8: _event_changed_8 = True; on_custom_event_8()
    else: _event_changed_8 = False

def on_custom_event_8():
    global time_s1
    oled.fill_rect(0, 48, 128, 16, 0)
    oled.DispChar("闹钟时间到了", 27, 46, 1)
    oled.show()
    while not button_b.value() == 0:
        music.play('D4:1')
        my_rgb.fill( (102, 0, 0) )
        my_rgb.write()
        time.sleep_ms(100)
        my_rgb.fill( (0, 0, 0) )
        my_rgb.write()
        time.sleep_ms(100)
    oled.fill_rect(0, 48, 128, 16, 0)


def nowWeather(apikey,location='ip',language='zh-Hans',unit='c'):         #设置天气实况返回的数据
    nowResult = urequests.get(url_now, params={
        'key': apikey,
        'location': location,
        'language': language,
        'unit': unit
    })
    json=nowResult.json()
    nowResult.close()
    return json

def dailyWeather(apikey,location='ip',language='zh-Hans',unit='c',start='0',days='5'):        #设置多日天气，只返回今日的数据
    dailyResult = urequests.get(url_daily, params={
        'key': apikey,
        'location': location,
        'language': language,
        'start': start,
        'days': days
    })
    json=dailyResult.json()
    dailyResult.close()
    return  json
    
    



def refresh():
    nowRsp=nowWeather(API_KEY)                 #通过API密钥获取天气实况
    dailyRsp=dailyWeather(API_KEY)             #通过API密钥获取多日天气预报

    today=dailyRsp['results'][0]['daily'][0]['date'][-5:]         #当前日期，显示“月-日”
    todayHigh=dailyRsp['results'][0]['daily'][0]['high']          #最高温度
    todaylow=dailyRsp['results'][0]['daily'][0]['low']            #最低温度

    nowText=nowRsp['results'][0]['now']['text']                   #天气现象文字
    nowTemper=nowRsp['results'][0]['now']['temperature']          #温度
    todayIco=nowRsp['results'][0]['now']['code']                  #天气现象图标
    city=nowRsp['results'][0]['location']['name']                 #地理位置

    oled.fill(0)
    oled.DispChar("%s,天气实况" %city,0,0)
    oled.DispChar(today,90,0)
    oled.DispChar("%s℃/%s" %(nowTemper,nowText),5,25)         #显示当前温度
    oled.DispChar("%s~%s℃" %(todaylow,todayHigh),75,25)       #显示今日最低、最高气温

    oled.show()

refresh()          #数据更新

tim1 = Timer(1)
tim1.init(period=1800000, mode=Timer.PERIODIC,callback=lambda _:refresh())      #定时，每半个钟刷新一次


while True:
    my_rgb.fill( (102, 102, 102) )
    my_rgb.write()                                                            #亮灯
    time_s1 = ''.join([str(x) for x in [time.localtime()[3] // 10, time.localtime()[3] % 10, ":", time.localtime()[4] // 10, time.localtime()[4] % 10, ":", time.localtime()[5] // 10, time.localtime()[5] % 10]])
    oled.DispChar(time_s1, 40, 47, 1)                                          #显示实时时间，实时更新
    oled.show()
    tim10.init(period=100, mode=Timer.PERIODIC, callback=timer10_tick)         #整点报时
    tim8.init(period=100, mode=Timer.PERIODIC, callback=timer8_tick)           #闹钟



