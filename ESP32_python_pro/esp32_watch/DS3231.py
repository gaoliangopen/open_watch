import network
import utime
import _thread
import math
import machine
import array
import json
import urequests
import sdcard, os

from machine import I2C,Pin,PWM,ADC,SPI
from ssd1306 import SSD1306_I2C
from mpu6050 import mpu6050  
from DS3231 import DS3231  
from wifiSet import connect

"""
lock = _thread.allocate_lock() #线程锁
semp = _thread.allocate_semephare() #信号量
"""

time_hour = 0
time_minute = 0
pow = 0   #电量剩余状态
key_1 = 1 #对应按键状态默认高电平
key_2 = 1 #对应按键状态默认高电平
key_3 = 1 #对应按键状态默认高电平
key_4 = 1 #对应按键状态默认高电平
tf_de = 1 #
interface_sign_up = 0 #当前顶层界面索引
interface_sign_down = 0 #底层界面索引

interruptCounter = 0 #中断计数

#定时设置界面需要
timer_parameter = {"选中":0,"时长":0,"计数":0,"状态":0,"重复":0}
#网络校时界面需要
time_calibration = {"选中":0,"状态":0,"ssid":"CMCC","password":"be"}
mpuArray = array.array("H",[0 for x in range(2)])#定义类似C语言的数组暂时空闲
#connect('CMCC-d5gQ','betdacbf')

def qs_parse(qs):
  parameters = {}
  ampersandSplit = qs.split("&")
  for element in ampersandSplit:
    equalSplit = element.split("=")
    parameters[equalSplit[0]] = equalSplit[1]
  return parameters

def inter_res():
  global interruptCounter
  global interface_sign_up
  
  state = machine.disable_irq()
  interruptCounter = 0
  machine.enable_irq(state)
  
def calibration_time():
  global interface_sign_down
  global key_1
  global key_2
  global key_3
  global key_4
  global tf_de
  dict = {}
  #按键检测部分
  if (key_1 == 0) and (time_calibration["选中"] == 1):
    time_calibration["状态"] = 1
    pass
  if (key_3 == 0):
    interface_sign_down = 1
    time_calibration["选中"] = 1
    pass
  if (key_4 == 0):
    time_calibration["选中"] = 0
    time_calibration["状态"] = 0
    interface_sign_down = 0
    utime.sleep_ms(500)
    key_4 = 1
    pass
  #逻辑部分
  if time_calibration["状态"] == 1:

    os.chdir("")#进入根目录
    f = open('WIFI.txt', "rb")
    ret = f.read()
    f.close()
    msg = str(ret,'utf-8')#bytes转字符串
    print(qs_parse(msg))
    time_calibration["ssid"] = qs_parse(msg)["S"]
    time_calibration["password"] = qs_parse(msg)["P"]
    oled.text("connect-wifi",0, 30)
    oled.show()
    msg = connect(time_calibration["ssid"],time_calibration["password"])
    if msg:
      oled.text("connect-success",0, 40)
      oled.show()
      url = 'http://quan.suning.com/getSysTime.do'
      res=urequests.get(url).text
      print(res)
      j=json.loads(res)
      t2_date = j['sysTime2'].split()[0] #日期
      t2_time = j['sysTime2'].split()[1] #时间
    #初始日期和时间，设置一次即可
      ds.DATE([int(x) for x in t2_date[2:].split('-')])   #设置初始日期年、月、日
      ds.TIME([int(x) for x in t2_time.split(':')])   #设置初始时间时、分、秒
      oled.text("ntp-success",0, 50)
      oled.show()
    else:
      oled.text("connect-failure",0, 40)
      oled.show()
      time_calibration["选中"] = 0
      time_calibration["状态"] = 0
      interface_sign_down = 0
    wifi = network.WLAN(network.STA_IF)  
    wifi.active(False)
    oled.text("off-wifi",0, 60)
    oled.show()
    utime.sleep_ms(500)

  #界面显示部分
  oled.fill(0)
  oled.text("NTP",50, 5)

  if time_calibration["选中"] == 1:
    oled.line(40,15,80,15,1) 
  else:
    oled.line(40,15,80,15,0) 
  oled.show()
  
def interface_main():
  global time_hour
  global time_minute
  global pow
  #读取日期分
  ds.DATE() 
  #读取时间
  ds.TIME()
  #读取温度
  ds.TEMP()
  oled.fill(0)

  #oled.char(0,0,0xFE)
  
  oled.text(str(ds.TIME()[0])+":"+str(ds.TIME()[1])+":"+str(ds.TIME()[2]), 35, 30) 
  pow = adc.read() - 1800
  pow = pow/600
  if pow > 1:
   pow = 1
  elif pow < 0:
   pow = 0 
  pow = math.floor(pow*100)
  oled.text("POW:"+str(pow)+"%",60, 5)
  oled.text(str(ds.DATE()[0])+"-"+str(ds.DATE()[1])+"-"+str(ds.DATE()[2]), 0, 5) 
  oled.text("TEMP:"+str(ds.TEMP()), 45, 55)
  
  oled.show()
  """
  if time_minute != ds.TIME()[1]:
    oled.fill(0)
    time_minute = ds.TIME()[1]
    oled.number(time_minute//10,9,2)
    oled.number(time_minute%10,11,2)
    oled.number(10,7,2) # :
    time_hour = ds.TIME()[0]
    oled.number(time_hour//10,3,2)
    oled.number(time_hour%10,5,2)
    pow = adc.read() - 1800
    pow = pow/600
    if pow > 1:
     pow = 1
    elif pow < 0:
     pow = 0 
    pow = math.floor(pow*100)
    oled.text("POW:"+str(pow)+"%",60, 5)
    oled.text(str(ds.DATE()[0])+"-"+str(ds.DATE()[1])+"-"+str(ds.DATE()[2]), 0, 5) 
    oled.text("TEMP:"+str(ds.TEMP()), 45, 55)
    oled.show()
  """
def interface_timer():
    global interface_sign_up
    global interface_sign_down
    global key_1
    global key_2
    global key_3
    global key_4  
    #按键处理部分
    if (key_1 == 0) and (timer_parameter["选中"] > 0):
      if timer_parameter["选中"] == 1:#选中标题按钮判断是否启动运行
        timer_parameter["状态"] = 1
        state = machine.disable_irq()
        timer_parameter["计数"] = 0
        machine.enable_irq(state)        
        pwm0.duty(100) # 设置占空比
        utime.sleep_ms(100)
        pwm0.duty(0) # 设置占空比
      elif timer_parameter["选中"] == 2: #分钟时长计算
        timer_parameter["时长"] += 1
      elif timer_parameter["选中"] == 3: #重复性选择
        timer_parameter["重复"] = 1
    elif (key_2 == 0) and (timer_parameter["选中"] > 0):
      if timer_parameter["选中"] == 1:#选中标题按钮判断是否启动运行
        timer_parameter["状态"] = 0
      elif timer_parameter["选中"] == 2: #分钟时长计算
        timer_parameter["时长"] -= 1

      elif timer_parameter["选中"] == 3: #重复性选择
        timer_parameter["重复"] = 0
      pass
    elif key_3 == 0:
      #pwm0.duty(200) # 设置占空比
      timer_parameter["选中"] += 1
      if timer_parameter["选中"] > 3:
        timer_parameter["选中"] = 1
        
      interface_sign_down = 1
      interface_sign_up = 1
      pass
    elif key_4 == 0:
      #pwm0.duty(0) # 设置占空比
      timer_parameter["选中"] = 0
      timer_parameter["状态"] = 0
      state = machine.disable_irq()
      timer_parameter["计数"] = 0
      machine.enable_irq(state)
      interface_sign_down = 0


      utime.sleep_ms(200)


      key_4 = 1
      pass
    else:
      pass


      


    #逻辑处理部分


    if timer_parameter["状态"] == 1:#判断是否运行状态


      if timer_parameter["时长"] <= timer_parameter["计数"]/60:


        pwm0.duty(200) # 设置占空比


        utime.sleep_ms(200)


        pwm0.duty(0) # 设置占空比


        if timer_parameter["重复"] == 1:
          state = machine.disable_irq()
          timer_parameter["计数"] = 0
          machine.enable_irq(state)
        else:
          timer_parameter["选中"] = 0


          timer_parameter["状态"] = 0


          state = machine.disable_irq()


          timer_parameter["计数"] = 0


          machine.enable_irq(state)
    #界面显示部分
    oled.fill(0)
    oled.text("TIMER",40, 5)
    if timer_parameter["选中"] == 1:
      oled.line(40,15,80,15,1) 
    if timer_parameter["状态"] == 1:
      residue_time = math.floor(timer_parameter["时长"]*60 - timer_parameter["计数"])
      oled.text(str(residue_time)+'s',90, 5) #如果运行状态显示倒计时
      
    oled.text("time:"+str(timer_parameter["时长"])+"min",0, 30)
    if timer_parameter["选中"] == 2:
      oled.line(0,40,128,40,1) 
    if timer_parameter["重复"] == 0:
      oled.text("repeat:"+"no",0, 50)
    elif timer_parameter["重复"] == 1:
      oled.text("repeat:"+"yes",0, 50)
      
    if timer_parameter["选中"] == 3:
      oled.line(0,60,128,60,1) 
    oled.show()
    
def oled_core():
  #interface_main()
  #interface_timer()
  global time_minute
  global interface_sign_up
  if interface_sign_up == 0 :
    interface_main()
  elif interface_sign_up == 1: #定时界面
    interface_timer()
  elif interface_sign_up == 2: #网络校时
    calibration_time()
  #print("adc = ",adc.read()) 
  #oled.chinese("关",0,0)
   
    
def oled_thread(time_):

  while True:
    """
    oled.text(str(adc.read()), 0, 20)
    oled.text(str(ds.TIME()[0])+":"+str(ds.TIME()[1])+":"+str(ds.TIME()[2]), 0, 35) 
    oled.text(str(ds.TEMP()), 0, 50) 
    oled.number(0,2,2)
    oled.show()
    oled.number(1,3,2)
    oled.show()
    oled.number(2,4,2)
    oled.show()
    """
    oled_core()
    utime.sleep_ms(time_)
    
def ds3231_thread(time_):
  while True: 
    utime.sleep_ms(time_)    
    
    
def mpu6050_thread(time_):
  global interface_sign_up
  global totalInterruptsCounter
  while True:
    
    if (interruptCounter > 10) and (interface_sign_down == 0):
      interface_sign_up = 0
      inter_res()
      oled.poweroff()

    mpuArray[0] = mpu.mpu6050_data()[3]
    if (mpuArray[0] > 60000) and (mpuArray[1] < 100) :
      oled.poweron()
      inter_res()
    mpuArray[1] = mpuArray[0]
    
    """
    print("ACCEL_XOUT_H",mpu.mpu6050_data()[0])
    print("ACCEL_YOUT_H",mpu.mpu6050_data()[1])
    print("ACCEL_ZOUT_H",mpu.mpu6050_data()[2])
    print("GYRO_XOUT_H",mpu.mpu6050_data()[3])
    print("GYRO_YOUT_H",mpu.mpu6050_data()[4])
    print("GYRO_ZOUT_H",mpu.mpu6050_data()[5])
    """
    utime.sleep_ms(time_)
    
def di_thread(time_):
  global key_1
  global key_2
  global key_3
  global key_4
  global tf_de
  
  global pow
  count = 0
  while True:
    key_1 = p27.value()
    key_2 = p14.value()
    key_3 = p12.value()
    key_4 = p13.value()
    tf_de = p15.value()
    count += 1
   
    if count > 600:
      count = 0
      print('pow:',pow)
    utime.sleep_ms(time_)

def do_thread(time_):
  global key_1
  global key_2
  global key_3
  global key_4
  global interface_sign_up
  global interface_sign_down
  while True:
    if (key_1 == 0) and (interface_sign_down == 0):
      oled.poweron()
      inter_res()
      if interface_sign_up < 2:
        interface_sign_up += 1
      #oled.contrast(255)
     # oled.poweroff()
      print("key_1",interface_sign_up)
    if (key_2 == 0) and (interface_sign_down == 0):
      oled.poweron()
      inter_res()
      if interface_sign_up > 1:
        interface_sign_up -= 1

      #oled.poweron()
      #oled.contrast(0)
      print("key_2",interface_sign_up)
    if (key_3 == 0) and (interface_sign_down == 0):
      oled.poweron()
      inter_res()
      #ds.DATE([19,12,7])
      #ds.TIME([23,11,13])
      print("key_3")
    if (key_4 == 0) and (interface_sign_down == 0):
      oled.poweron()
      interface_sign_up = 0
      inter_res()
      print("key_4")
    utime.sleep_ms(time_)
    

	
def handleInterrupt(timer):
  
  global interruptCounter
  interruptCounter = interruptCounter+1 
  
  if timer_parameter["状态"] == 1: #用于定时使用
    timer_parameter["计数"] += 1
    
ds = DS3231()
#ds.DATE([19,12,7])
#ds.TIME([23,11,13])
mpu = mpu6050()

mic0Pin = Pin(32,Pin.IN)
adc = ADC(mic0Pin)
adc.atten(ADC.ATTN_11DB)

i2c = I2C(-1,scl=Pin(21), sda=Pin(22),freq=40000000)
oled = SSD1306_I2C(128, 64, i2c)
  
p27 = Pin(27,Pin.IN,Pin.PULL_UP)
p14 = Pin(14,Pin.IN,Pin.PULL_UP)
p12 = Pin(12,Pin.IN,Pin.PULL_UP)
p13 = Pin(13,Pin.IN,Pin.PULL_UP)
p15 = Pin(15,Pin.IN,Pin.PULL_UP)


pwm0 = PWM(Pin(4)) # 通过Pin对象来创建PWM对象
pwm0.freq() # 获得当前的PWM频率
pwm0.duty(0) # 获得当前的PWM占空比

timer = machine.Timer(0)
timer.init(period=1000, mode=machine.Timer.PERIODIC, callback=handleInterrupt)

if p15.value() == 0:
  sd = sdcard.SDCard(SPI(2, sck=Pin(18), mosi=Pin(23), miso=Pin(19)), Pin(5))
  os.mount(sd,'/sd') #挂载SD卡
  os.chdir("sd")#进入sd卡子目录
  f = open('WIFI.txt', "rb")
  ret = f.read()
  f.close()
  msg = str(ret,'utf-8')#bytes转字符串
  
  os.chdir("")#进入根目录
  f = open("WIFI.txt", "w")
  f.write("msg")
  f.close()
  print("SDCard_sun")
#wifi = network.WLAN(network.STA_IF)
#wifi.active(False)
#machine.freq(160000000)     # 设置当前CPU频率
_thread.start_new_thread(oled_thread, (200,))
_thread.start_new_thread(ds3231_thread, (800,))
_thread.start_new_thread(mpu6050_thread, (500,))
_thread.start_new_thread(do_thread, (100,))
_thread.start_new_thread(di_thread, (100,))

while True:
        pass
        
"""

i2c = I2C(-1,scl=Pin(21), sda=Pin(22),freq=400000)
oled = SSD1306_I2C(128, 64, i2c)
oled.fill(1)
oled.show()
oled.fill(0)
oled.show()


from mpu6050 import mpu6050  
aa = mpu6050()

import utime
import wifiSet
from machine import I2C,Pin,PWM,ADC
from ssd1306 import SSD1306_I2C
from DS3231 import DS3231  
wifiSet.connect()
i2c = I2C(-1,scl=Pin(22), sda=Pin(23),freq=400000)
oled = SSD1306_I2C(128, 64, i2c)
oled.fill(1)
oled.show()
oled.fill(0)
oled.show()
ds = DS3231()

#22 23 18 19
p16 = Pin(16,Pin.IN,Pin.PULL_UP)
p15 = Pin(15,Pin.IN,Pin.PULL_UP)
p14 = Pin(14,Pin.IN,Pin.PULL_UP)
p13 = Pin(13,Pin.IN,Pin.PULL_UP)
p12 = Pin(12,Pin.IN,Pin.PULL_UP)
p5 = Pin(5,Pin.IN,Pin.PULL_UP)

adc = ADC(Pin(32)) 
adc.read()

pwm0 = PWM(Pin(4)) # 通过Pin对象来创建PWM对象
pwm0.freq() # 获得当前的PWM频率
pwm0.freq(1000) # 设置PWM频率
pwm0.duty() # 获得当前的PWM占空比
pwm0.duty(200) # 设置占空比





i = 0


ds.DATE([19,12,7])
ds.TIME([23,11,13])





while True:


  print("000")


  utime.sleep_ms(100) 


  print("111")
  #读取日期
  ds.DATE() 
  #读取时间
  ds.TIME()
  #读取温度
  ds.TEMP()
  oled.fill(0)
  oled.text(str(ds.DATE()), 0, 20)
  oled.text(str(ds.TIME()), 0, 35) 
  oled.text(str(ds.TEMP()), 0, 50)
  oled.show() 
  



  aa.mpu6050_test()
  time.sleep_ms(500) 
  i = i + 50
  if i > 1000:
    i = 0
  pwm0.duty(i) # 设置占空比
  print("adc = ",adc.read())
  if p16.value() == 0:
    print("p16 = ",p16.value())
  if p15.value() == 0:
    print("p15 = ",p15.value())
  if p14.value() == 0:
    print("p14 = ",p14.value())
  if p13.value() == 0:
    print("p13 = ",p13.value())
  if p12.value() == 0:
    print("p12 = ",p12.value())
  if p5.value() == 0:
    print("p5 = ",p5.value())

  

  
  oled.text(str(ds.DATE()), 0, 20)
  oled.text(str(ds.TIME()), 0, 35) 
  oled.text(str(ds.TEMP()), 0, 50)
  #oled.chinese('关',0,0)
  
  oled.show() 

oled.invert(True)
oled.invert(False)
"""




















