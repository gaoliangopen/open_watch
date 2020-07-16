"""
import _thread
import time

def test3Thread(description,count):
  print(description)
  i = 0
  while i < count:
    print("nihao"+str(i))
    i = i+1
    time.sleep(2)
  
_thread.start_new_thread(test3Thread,("wfgz",5))

"""
"""
import machine

interruptsCounter = 0
totalInterruptsCounter = 0
timer = machine.Timer(0) #新建立一个定时器对象 使用定时器0 0~3

def handleInterrupt(timer):
  global interruptsCounter
  interruptsCounter = interruptsCounter + 1
timer.init(period=1000,mode=machine.Timer.PERIODIC,callback = handleInterrupt)

while True:
  if interruptsCounter>0:
    state = machine.disable_irq()
    interruptsCounter = interruptsCounter - 1
    machine.enable_irq(state)
    totalInterruptsCounter = totalInterruptsCounter + 1
    print("interrupt has occurred:" + str(totalInterruptsCounter))
    
"""
import machine
interruptCounter = 0
totalInterruptsCounter = 0

def callback(pin):
  global interruptCounter
  interruptCounter = interruptCounter + 1

p25 = machine.Pin(25,machine.Pin.IN,machine.Pin.PULL_UP)
p25.irq(trigger=machine.Pin.IRQ_FALLING,handler=callback)
while True:
  if interruptCounter > 0:
    state = machine.disable_irq()
    interruptCounter = interruptCounter - 1
    machine.enable_irq(state)
    totalInterruptsCounter = totalInterruptsCounter + 1
    print("Interrupt"+ str(totalInterruptsCounter))

