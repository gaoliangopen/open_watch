import network
import utime
import urequests
import machine

def connect(ssid,password):
  wifi = network.WLAN(network.STA_IF)
  #判断是否已经连接，wifi.isconnected() 是Flash
  if not wifi.isconnected():
    print ("already connected")
    # 激活WIFI，开始扫描周围SSID
    wifi.active(True)
    # 指定连接WiFi
    wifi.connect(ssid,password)
    while not wifi.isconnected():
      utime.sleep(1)
    print("connect ok",wifi.ifconfig())   
    
"""  
def setTime() -> None:
  for i int range(2):
    try:
        rtc = machine.RTC()
        response = urequests.get("https://www.gamefunc.top/getCtime")
        rtc.init(tuple(ujson.loads(response.text)))
        print(utime.localtime())
        del response
        break
      except:
        utime.sleep(5)
  """        
          
          
          
          
          
          


