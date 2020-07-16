
from machine import Pin,I2C
import time

I2C_WRITE_ADDR      = const(0xAE)
I2C_READ_ADDR       = const(0xAF)

REG_INTR_STATUS_1   = const(0x00)
REG_INTR_STATUS_2   = const(0x01)
REG_INTR_ENABLE_1   = const(0x02)
REG_INTR_ENABLE_2   = const(0x03)
REG_FIFO_WR_PTR     = const(0x04)
REG_OVF_COUNTER     = const(0x05)
REG_FIFO_RD_PTR     = const(0x06)
REG_FIFO_DATA       = const(0x07)
REG_FIFO_CONFIG     = const(0x08)
REG_MODE_CONFIG     = const(0x09)
REG_SPO2_CONFIG     = const(0x0A)
REG_LED1_PA         = const(0x0C)
REG_LED2_PA         = const(0x0D)
REG_PILOT_PA        = const(0x10)
REG_MULTI_LED_CTRL1 = const(0x11)
REG_MULTI_LED_CTRL2 = const(0x12)
REG_TEMP_INTR       = const(0x1F)
REG_TEMP_FRAC       = const(0x20)
REG_TEMP_CONFIG     = const(0x21)
REG_PROX_INT_THRESH = const(0x30)
REG_REV_ID          = const(0xFE)
REG_PART_ID         = const(0xFF)

class max30102(object):
    uch_dummy = 0
    n_brightness = 0
    un_min = 0x3FFFF
    un_max = 0
    n_ir_buffer_length = 500
    
    def __init__(self):
      self.p0 = Pin(17,Pin.IN)
      self.i2c = I2C(-1,scl=Pin(15), sda=Pin(2),freq=50000)
      self.i2c_address = self.i2c.scan()[0]
      print(self.i2c_address)
      self.maxim_max30102_reset()
      time.sleep_ms(10) 
      uch_dummy = self.maxim_max30102_read_reg(0)
      self.maxim_max30102_init()
      
      for i in range(n_ir_buffer_length):
        while self.p0.value():
          print("1111")
          
    
    def maxim_max30102_write_reg(self,uch_addr,uch_data):
      buf = bytearray(2)
      buf[0] = uch_addr
      buf[1] = uch_data
      self.i2c.writeto(I2C_WRITE_ADDR, buf)
      
    def maxim_max30102_read_reg(self,uch_addr):
      buf = bytearray(1)
      buf[0] = uch_addr
      self.i2c.writeto(I2C_WRITE_ADDR, buf)
      t = self.i2c.readfrom(I2C_READ_ADDR,1)[0]
      return t
      
    
    def maxim_max30102_reset(self):
      self.maxim_max30102_write_reg(REG_MODE_CONFIG,0x40)
      
    def maxim_max30102_init(self):
      self.maxim_max30102_write_reg(REG_INTR_ENABLE_1,0xc0)
      self.maxim_max30102_write_reg(REG_INTR_ENABLE_2,0x00)
      self.maxim_max30102_write_reg(REG_FIFO_WR_PTR,0x00)
      self.maxim_max30102_write_reg(REG_OVF_COUNTER,0x00)
      self.maxim_max30102_write_reg(REG_FIFO_RD_PTR,0x00)
      self.maxim_max30102_write_reg(REG_FIFO_CONFIG,0x0f)
      self.maxim_max30102_write_reg(REG_MODE_CONFIG,0x03)
      self.maxim_max30102_write_reg(REG_SPO2_CONFIG,0x27)
      self.maxim_max30102_write_reg(REG_LED1_PA,0x24)
      self.maxim_max30102_write_reg(REG_LED2_PA,0x24)
      self.maxim_max30102_write_reg(REG_PILOT_PA,0x7f)
      
      
        
      
