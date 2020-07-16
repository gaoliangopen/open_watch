from machine import I2C,Pin,PWM,ADC,SPI
pwm0 = PWM(Pin(4)) # 通过Pin对象来创建PWM对象
pwm0.freq() # 获得当前的PWM频率
pwm0.duty(0) # 获得当前的PWM占空比
print("hello word")
"""
from mpu6050 import mpu6050  
mpu = mpu6050()
"""
