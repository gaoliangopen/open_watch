import json
import utime
import math
import machine
from machine import I2C,Pin,PWM,ADC,SPI
from ssd1306 import SSD1306_I2C
from DS3231 import DS3231  
from mpu6050 import mpu6050  
from wifiSet import connect

#timer_1 = [30*60,45*60,5*60,10*60,0]
timer_1 = [0,0,0,0,0]
timer_2 = [70,0,0]
timer_3 = [0,0,99]


ds = DS3231()


#如果时钟为0，进行网络校时

#ds.DATE([20,8,16])
#ds.TIME([16,27,00])
mpu = mpu6050()

i2c = I2C(-1,scl=Pin(25), sda=Pin(26),freq=40000000)
oled = SSD1306_I2C(128, 64, i2c)

mic0Pin = Pin(32,Pin.IN)
adc = ADC(mic0Pin)
adc.atten(ADC.ATTN_11DB)

k0_p27 = Pin(27,Pin.IN,Pin.PULL_UP)
k1_p14 = Pin(14,Pin.IN,Pin.PULL_UP)
k2_p12 = Pin(12,Pin.IN,Pin.PULL_UP)
k3_p13 = Pin(13,Pin.IN,Pin.PULL_UP)


pwm0 = PWM(Pin(4)) # 通过Pin对象来创建PWM对象
pwm0.freq() # 获得当前的PWM频率
pwm0.duty(0) # 获得当前的PWM占空比

device_state = 0 #设备状态 0：空白 1：计时完成/息屏 2：清空计时（执行）
counter_0 = 0   #用于屏保计时
counter_1 = 0   #用于频率区分
r_buffer = [0,0,0,0,0,0]
s_buffer = 0

if ds.TIME()[0] == 0:
  msg = connect()
  t2_date = msg[0] #日期
  t2_time = msg[1] #时间
  ds.DATE([int(x) for x in t2_date[2:].split('-')])   #设置初始日期年、月、日
  ds.TIME([int(x) for x in t2_time.split(':')])   #设置初始时间时、分、秒
  
"""
timer = machine.Timer(0)  
timer.init(period=100, mode=machine.Timer.PERIODIC, callback=handleInterrupt)
"""
machine.freq(20000000)     # 设置当前CPU频率    

def dial_instrument(time,radius):
    # 1象限
  t = []
  if time < 16 : 
    x = radius*math.cos((math.pi/30)*(15 - time))
    y = radius*math.sin((math.pi/30)*(15 - time))
    x = x + 96
    y = 32 - y
    
  # 4象限
  elif time < 31 :
    x = radius*math.cos((math.pi/30)*(time - 15))
    y = radius*math.sin((math.pi/30)*(time - 15))
    x = x + 96
    y = y + 32

  # 3象限
  elif time< 46 :
    x = radius*math.cos((math.pi/30)*(45 - time))
    y = radius*math.sin((math.pi/30)*(45 - time))
    x = 96 - x
    y = y + 32
    
  # 2象限 
  elif time < 61 :
    x = radius*math.cos((math.pi/30)*(time - 45))
    y = radius*math.sin((math.pi/30)*(time - 45))
    x = 96 - x
    y = 32 - y
    
  t.append(x)
  t.append(y)
  return t

def key_test():
  global device_state
  global counter_0
  
  if k3_p13.value() == 0: #左边按键
    if device_state == 1:
      counter_0 = 0
      device_state = 0
      oled.poweron()
    else:
      counter_0 = 200
      oled.poweroff()
      device_state = 1
  
  if device_state != 1:
    if k1_p14.value() == 0: #右边 第1个
      if timer_3[0] > 0:
        timer_3[0] = 0
      timer_1[0] = timer_1[0] + 60*5
      counter_0 = 0
    
    if k2_p12.value() == 0: #右边 第2个
      if timer_3[0] > 0:
        timer_3[0] = 0
      if timer_1[0] > 0:
        timer_1[0] = timer_1[0] - 60*5
      counter_0 = 0
      
    if k0_p27.value() == 0: #右边 第3个
      counter_0 = 0
      if timer_1[0] > 0:
        timer_3[0] = timer_1[0]
        timer_3[1] = 0
        timer_3[2] = ds.TIME()[2]
        timer_1[0] = 0
      elif timer_2[0] != 70:
          timer_2[0] = 70
          timer_2[1] = 0
          timer_2[2] = 0
      else:
        timer_2[0] = ds.TIME()[0]
        timer_2[1] = ds.TIME()[1]
        timer_2[2] = ds.TIME()[2]
while 1:


#按键部分
#**************************************************************
  utime.sleep_ms(600)
  key_test() 
  
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ 
  
#陀螺仪检测
#**************************************************************
  if mpu.mpu6050_data()[1] > 64000 and mpu.mpu6050_data()[2] > 15404: 
    if counter_0 > 199:
      counter_0 = 0
      device_state = 0
      oled.poweron()
      
 
  """ 
  print("ACCEL_XOUT_H",mpu.mpu6050_data()[0])
  print("ACCEL_YOUT_H",mpu.mpu6050_data()[1])
  print("ACCEL_ZOUT_H",mpu.mpu6050_data()[2])
  print("GYRO_XOUT_H",mpu.mpu6050_data()[3])
  print("GYRO_YOUT_H",mpu.mpu6050_data()[4])
  print("GYRO_ZOUT_H",mpu.mpu6050_data()[5])
  """
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ 
  
  oled.fill(0)  
  
#像素点
#************************************************************** 
  #oled.pixel(62+int(32*(mpu.mpu6050_data()[2]/65535)),1+int(62*(mpu.mpu6050_data()[1]/65535)),1)
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ 

#表盘  
#**************************************************************  

  oled.line(65,1,127,1,1)
  oled.line(127,1,127,63,1)
  oled.line(127,63,65,63,1)
  oled.line(65,63,65,1,1)
 
  oled.line(65,32,68,32,1)
  oled.line(65,19,67,19,1)
  oled.line(65,45,67,45,1)
  
  oled.line(124,32,127,32,1)
  oled.line(125,19,127,19,1)
  oled.line(125,45,127,45,1) 
 
  oled.line(95,1,95,3,1)
  oled.line(96,1,96,4,1)
  oled.line(97,1,97,3,1)
  oled.line(83,1,83,3,1)
  oled.line(109,1,109,3,1)
  
  oled.line(96,59,96,63,1)
  oled.line(83,60,83,63,1)
  oled.line(109,60,109,63,1)
  
  oled.pixel(96,32,1)
  oled.pixel(95,32,1)
  oled.pixel(97,32,1)
  oled.pixel(96,31,1)
  oled.pixel(96,33,1)
  oled.pixel(95,31,1)
  oled.pixel(97,31,1)
  oled.pixel(95,33,1)
  oled.pixel(97,33,1)
  
  for i in range(25):
    oled.pixel(int(127*i/24),0,1)
  
  oled.line(0,0,int(127*(ds.TIME()[0]/24)),0,1)
  s_buffer = ds.TIME()[0]
  if s_buffer > 12:
    s_buffer = s_buffer - 12
  else:
    s_buffer = s_buffer 

  r_buffer = dial_instrument(s_buffer*5 + int(5*ds.TIME()[1]/60),15)
  x = r_buffer[0]
  y = r_buffer[1]
  oled.line(96,32,int(x),int(y),1) #时针
 
  
  r_buffer = dial_instrument(ds.TIME()[1],18)
  x = r_buffer[0]
  y = r_buffer[1]
  
  oled.line(96,32,int(x),int(y),1) #分针
  r_buffer = dial_instrument(ds.TIME()[2],22)
  x = r_buffer[0]
  y = r_buffer[1]
  oled.line(96,32,int(x),int(y),1) #秒针


  #print(str(ds.TIME()[1])+str(ds.TIME()[2]))
  #oled.text(str(ds.DATE()[0])+"-"+str(ds.DATE()[1])+"-"+str(ds.DATE()[2]), 60, 42) 
  #oled.text(str(ds.TIME()[0])+":"+str(ds.TIME()[1])+":"+str(ds.TIME()[2]), 60, 52) 
# //////////////////////////////////////////////////////////////// 
  
   
#计时温度等部分    
#****************************************************************  

  oled.line(50,1,50,62,1) 
  oled.line(0,32,50,32,1)
  oled.line(0,1,0,64,1)
  oled.line(0,1,50,1,1)
  oled.line(0,63,50,63,1)
  
  if timer_3[0] > 0:
    
    if timer_3[2] != ds.TIME()[2]:
      timer_3[2] = ds.TIME()[2]
      timer_3[0] = timer_3[0] - 1
    pow =timer_3[0]
    oled.text("CDOWN:",2, 8)
    oled.text(str(pow//60)+":"+str(pow%60),2, 18)
    if timer_3[0] == 0:
      timer_1[0] = 0
      pwm0.duty(100) # 设置占空比
      utime.sleep_ms(500)
      pwm0.duty(0) # 设置占空比

  elif timer_3[1] > 0:
    if timer_3[2] != ds.TIME()[2]:
      timer_3[2] = ds.TIME()[2]
      timer_3[1] = timer_3[1] - 1
    pow =timer_3[1]
    oled.text("CDOWN:",0, 8)
    oled.text(str(pow//60)+":"+str(pow%60),2, 18)
    if timer_3[1] == 0:
      pwm0.duty(100) # 设置占空比
      utime.sleep_ms(500)
      pwm0.duty(0) # 设置占空比
  else:  
    if counter_0 < 300: #5分钟更新一次
      timer_3[2] = 99
      pow = adc.read() - 1800
      pow = pow/600
      if pow > 1:
       pow = 1
      elif pow < 0:
       pow = 0 
      pow = math.floor(pow*100)
      
    if k2_p12.value() == 0 or k1_p14.value() == 0:
      oled.text("CDOWN:",2, 8)
      oled.text(str(timer_1[0]//60)+":"+str(timer_1[0]%60),2, 18)

    else:
      oled.text("POW:",2, 8)
      oled.text(str(pow)+"%",2, 18)
  counter_1 = counter_1 + 1
  if counter_1 < 3:
    oled.text("TEMP:", 2, 40)
    oled.text(str(ds.TEMP()-5), 2, 50)
  elif counter_1 < 6:
    oled.text(str(ds.DATE()[1])+"-"+str(ds.DATE()[2]), 2, 40) 
    oled.text(str(ds.TIME()[0])+":"+str(ds.TIME()[1]), 2, 50)  
  elif counter_1 < 9:
    oled.text("TEMP:", 2, 40)
    oled.text(str(ds.TEMP()-5), 2, 50)
    counter_1 = 0
  else:
    counter_1 = 0
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\  
 
 #oled.text(str(ds.DATE()[0])+"-"+str(ds.DATE()[1])+"-"+str(ds.DATE()[2]), 60, 42) 
  #oled.text(str(ds.TIME()[0])+":"+str(ds.TIME()[1])+":"+str(ds.TIME()[2]), 60, 52)  
 
#息屏倒计时部分 
#device_state 0：空白 1：计时完成/息屏 2：清空计时（执行）
#*********************************************************************** 


  if counter_0 > 200:
    oled.fill(0)
    oled.show() 
    counter_0 = 200 
    device_state = 1 #计时完成
    oled.poweroff()
    """
    if counter_0 > 360:
      counter_0 = 300      
    oled.fill(0)
    oled.line((counter_0 - 300)*2,counter_0 - 300,(counter_0 - 299)*2,counter_0 - 300,1)
    if ((counter_0 - 300) % 2) > 0:
      oled.fill(0)
  """  
  else:
    oled.show() 
    
  counter_0 = counter_0 + 1    
  
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ 

  
  
  












