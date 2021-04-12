import RPi.GPIO as GPIO
import time
import subprocess
import shlex

LED_RIGHT_PIN = 23
LED_LEFT_PIN = 24

SERVO_MOTER_PIN = 4
FREQ = 50
SERVO_MOTER = None

MOTER_PIN_1 = 20
MOTER_PIN_2 = 26

STARTUP_DONE = False
#######################################
# 起動処理
#######################################
def functionStartUp():
    print("functionStartUp")
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LED_RIGHT_PIN, GPIO.OUT)
    GPIO.setup(LED_LEFT_PIN, GPIO.OUT)

    GPIO.setup(SERVO_MOTER_PIN, GPIO.OUT)
    SERVO_MOTER = GPIO.PWM(SERVO_MOTER_PIN, FREQ)
    SERVO_MOTER.start(0.0)

    GPIO.setup(LED_RIGHT_PIN, GPIO.OUT)
    GPIO.setup(LED_LEFT_PIN, GPIO.OUT)

    GPIO.setup(MOTER_PIN_1, GPIO.OUT)
    GPIO.setup(MOTER_PIN_2, GPIO.OUT)
    
    STARTUP_DONE = True

#######################################
# 終了処理
#######################################
def funcitonEnd():
    print("functionEnd")
    
    functionSuspension()
    
    GPIO.output(LED_RIGHT_PIN, 0)
    GPIO.output(LED_LEFT_PIN, 0)
    
    GPIO.cleanup()
    
    STARTUP_DONE = False
    
#######################################
# 前進処理
#######################################
def functionDrive():
    print("functionDrive")

    GPIO.output(MOTER_PIN_1, GPIO.HIGH)
    GPIO.output(MOTER_PIN_2, GPIO.LOW)
    
#######################################
# 停止処理
#######################################
def functionSuspension():
    print("functionSuspension")

    GPIO.output(MOTER_PIN_1, GPIO.LOW)
    GPIO.output(MOTER_PIN_2, GPIO.LOW)
#######################################
# 後退処理
#######################################
def functionBack():
    print("functionBack")

    GPIO.output(MOTER_PIN_1, GPIO.LOW)
    GPIO.output(MOTER_PIN_2, GPIO.HIGH)

#######################################
# 直進処理
#######################################
def functionStraight():
    print("functionStraight")
    global SERVO_MOTER
    SERVO_MOTER.ChangeDutyCycle(0.0)
    
#######################################
# 右旋回処理
#####################################d##
def functionRightTurn():
    print("functionRightTurn")
    global SERVO_MOTER
    SERVO_MOTER.ChangeDutyCycle(2.5)

#######################################
# 左旋回処理
######################################d#
def functionLeftTurn():
    print("functionLeftTurn")
    global SERVO_MOTER
    SERVO_MOTER.ChangeDutyCycle(12.0)

#######################################
# カメラ起動処理
#######################################
def functionStartCamera():
    print("functionStartCamera")
    
    args = shlex.split("./momo --no-audio-device test")
    ret = subprocess.Popen(args)
    
    print(ret)

#######################################
# カメラ終了処理
#######################################
def functionStopCamera():
    print("functionStopCamera")

functionStartUp()
time.sleep(5)
functionDrive()
time.sleep(5)
functionSuspension()
time.sleep(5)
functionBack()
time.sleep(5)
functionSuspension()

funcitonEnd()