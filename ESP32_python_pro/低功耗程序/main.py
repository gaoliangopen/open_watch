import utime
import math
import machine
from machine import I2C,Pin,PWM,ADC,SPI
from ssd1306 import SSD1306_I2C
from DS3231 import DS3231  
from mpu6050 import mpu6050  

timer_1 = [30*60,45*60,5*60,10*60,0]
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

device_state = 0 #设备状态
counter_0 = 0   #用于屏保

interruptCounter = 0
def handleInterrupt(timer):
  global interruptCounter
  interruptCounter = interruptCounter+1
  
timer = machine.Timer(0)  
timer.init(period=100, mode=machine.Timer.PERIODIC, callback=handleInterrupt)

machine.freq(160000000)     # 设置当前CPU频率
while 1:

    
  if k3_p13.value() == 0:
    if counter_0 > 300:
      counter_0 = 0
    elif device_state > 0:
      oled.poweron()
      machine.freq(160000000)     # 设置当前CPU频率
      device_state = 0
      counter_0 = 0
      utime.sleep_ms(1000) #防止过度按压
    else:   
      oled.poweroff()
      machine.freq(20000000)     # 设置当前CPU频率
      device_state = 1
  
  if device_state == 0:  
    if k1_p14.value() == 0:
      timer_3[0] = timer_1[0]
      timer_3[1] = timer_1[2]
      timer_3[2] = ds.TIME()[2]
      counter_0 = 0
    
    if k2_p12.value() == 0:
      timer_3[0] = timer_1[1]
      timer_3[1] = timer_1[3]
      timer_3[2] = ds.TIME()[2]
      counter_0 = 0
      

    if k0_p27.value() == 0:
      counter_0 = 0
      if timer_2[0] != 70:
          timer_2[0] = 70
          timer_2[1] = 0
          timer_2[2] = 0
      else:
        timer_2[0] = ds.TIME()[0]
        timer_2[1] = ds.TIME()[1]
        timer_2[2] = ds.TIME()[2]
     
    oled.fill(0)
    
    oled.line(50,0,50,64,1) 

    oled.line(0,32,128,32,1)
    
    oled.text(str(ds.DATE()[0])+"-"+str(ds.DATE()[1])+"-"+str(ds.DATE()[2]), 60, 42) 
    oled.text(str(ds.TIME()[0])+":"+str(ds.TIME()[1])+":"+str(ds.TIME()[2]), 60, 52) 
    
    oled.text("ACLOCK:", 60, 5) 
    if timer_2[0] != 70:
      oled.text(str(timer_2[0])+":"+str(timer_2[1])+":"+str(timer_2[2]), 60, 15) 
    else:
      oled.text("NO", 60, 15) 
      
    if timer_3[0] > 0:
      
      if timer_3[2] != ds.TIME()[2]:
        timer_3[2] = ds.TIME()[2]
        timer_3[0] = timer_3[0] - 1
      pow =timer_3[0]
      oled.text("CDOWN:",0, 5)
      oled.text(str(pow//60)+":"+str(pow%60),0, 15)
      if timer_3[0] == 0:
        pwm0.duty(100) # 设置占空比
        utime.sleep_ms(500)
        pwm0.duty(0) # 设置占空比
        
        
    elif timer_3[1] > 0:
      if timer_3[2] != ds.TIME()[2]:
        timer_3[2] = ds.TIME()[2]
        timer_3[1] = timer_3[1] - 1
      pow =timer_3[1]
      oled.text("CDOWN:",0, 5)
      oled.text(str(pow//60)+":"+str(pow%60),0, 15)
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
      oled.text("POW:",0, 5)
      oled.text(str(pow)+"%",0, 15)
    
    oled.text("TEMP:", 0, 42)
    oled.text(str(ds.TEMP()), 0, 52)

    if counter_0 > 300:
      if counter_0 > 360:
        counter_0 = 300

      oled.fill(0)
      oled.line((counter_0 - 300)*2,counter_0 - 300,(counter_0 - 295)*2,counter_0 - 300,1)
      if ((counter_0 - 300) % 2) > 0:
        oled.fill(0)
    oled.show()    

    counter_0 = counter_0 + 1 
    utime.sleep_ms(500)
  
  else:
    utime.sleep_ms(3000)
    
  #闹钟
  if ds.TIME()[0] == timer_2[0]:
    if ds.TIME()[1] == timer_2[1]:
      if ds.TIME()[2] == timer_2[2]:
        pwm0.duty(100) # 设置占空比
        utime.sleep_ms(700)
        pwm0.duty(0) # 设置占空比   





