import sys
import RPi.GPIO as GPIO
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import time
import json
import subprocess
import shlex

###########################################
# AWS IoT 接続情報
###########################################
# モノの名前
MQTT_CLIENT = 'mini4wd'
# エンドポイントのURL
ENDPOINT_URL = 'a3042qvtxfzkab-ats.iot.us-east-2.amazonaws.com'
# エンドポイントのポート番号
ENDPOINT_PORT = 8883
# ルート証明書ファイル
ROOT_CA_PATH = 'cert/rootCA.pem'
# 個別秘密鍵ファイル
PRIVATE_KEY_PATH = 'cert/72fc0cbd23-private.pem.key'
# 個別証明書ファイル
PRIVATE_CERT_PATH = 'cert/72fc0cbd23-certificate.pem.crt'

# トピック名
TOPIC_NAME = 'testTopic'

## 受信コマンド
STARTUP_COMMAND = "startup"
CAMERA_ON_COMMAND = "cameraOn"
CAMERA_OFF_COMMAND = "cameraOff"
MOVE_COMMAND = "move"
STOP_COMMAND = "stop"
BACK_COMMAND = "back"
STRAIGHT_COMMAND = "straight"
LEFT_COMMAND = "left"
RIGHT_COMMAND = "right"
END_COMMAND = "end"

###########################################
# momo 起動情報
###########################################
MOMO_COMMAND = "./momo --no-audio-device test"
#MOMO_COMMAND = "./momo --no-audio-device ayame wss://ayame-labo.shiguredo.jp/signaling zenithfull@mini4-room --signaling-key Nlqlm3fKd-ABK5IPoM0LS3pSPgu0DB8o_vNqB1OOahbRn634"
###########################################
# GPIO 情報
###########################################
# LEDライト
LED_RIGHT_PIN = 13
LED_LEFT_PIN = 5
# サーボモーター
SERVO_MOTER_PIN = 7
SERVO_FREQ = 50
# モータードライバ
MOTER_PIN_1 = 21
MOTER_PIN_2 = 26

# モーター周波数
MOTER_FREQ = 50

## I/O コントローラ
SERVO_MOTER = None
MQTT_CLIENT = None
MOTOR_1 = None
MOTOR_2 = None

STARTUP_DONE = False
#######################################
# 起動処理
#######################################
def functionStartUp():
    global STARTUP_DONE
    if STARTUP_DONE == False:
        print("functionStartUp")
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(LED_RIGHT_PIN, GPIO.OUT)
        GPIO.setup(LED_LEFT_PIN, GPIO.OUT)

        global SERVO_MOTER
        GPIO.setup(SERVO_MOTER_PIN, GPIO.OUT)
        SERVO_MOTER = GPIO.PWM(SERVO_MOTER_PIN, SERVO_FREQ)
        SERVO_MOTER.start(0.0)

        GPIO.setup(MOTER_PIN_1, GPIO.OUT)
        GPIO.setup(MOTER_PIN_2, GPIO.OUT)

        global MOTOR_1
        MOTOR_1 = GPIO.PWM(MOTER_PIN_1, MOTER_FREQ)
        MOTOR_1.start(0)

        global MOTOR_2
        MOTOR_2 = GPIO.PWM(MOTER_PIN_2, MOTER_FREQ)
        MOTOR_2.start(0)

        GPIO.output(LED_RIGHT_PIN, GPIO.HIGH)
        GPIO.output(LED_LEFT_PIN, GPIO.HIGH)

        STARTUP_DONE = True

#######################################
# 終了処理
#######################################
def funcitonEnd():
    global STARTUP_DONE
    if STARTUP_DONE == True:
        print("functionEnd")
        
        functionSuspension()
        
        GPIO.output(LED_RIGHT_PIN, GPIO.LOW)
        GPIO.output(LED_LEFT_PIN, GPIO.LOW)
        
        STARTUP_DONE = False
    
#######################################
# 前進処理
#######################################
def functionDrive():
    global STARTUP_DONE
    if STARTUP_DONE == True:
        print("functionDrive")

        global MOTOR_1
        MOTOR_1.ChangeDutyCycle(0)
        global MOTOR_2
        MOTOR_2.ChangeDutyCycle(20)
    
#######################################
# 停止処理
#######################################
def functionSuspension():
    global STARTUP_DONE
    if STARTUP_DONE == True:
        print("functionSuspension")

        global MOTOR_1
        MOTOR_1.ChangeDutyCycle(0)
        global MOTOR_2
        MOTOR_2.ChangeDutyCycle(0)
#######################################
# 後退処理
#######################################
def functionBack():
    global STARTUP_DONE
    if STARTUP_DONE == True:
        print("functionBack")

        global MOTOR_1
        MOTOR_1.ChangeDutyCycle(20)
        global MOTOR_2
        MOTOR_2.ChangeDutyCycle(0)

#######################################
# サーボモータの角度設定処理
#######################################
def servo_angle(angle):
    global SERVO_MOTER
    duty = 2.5 + (12.0 - 2.5) * (angle + 90) / 180   #角度からデューティ比を求める
    SERVO_MOTER.ChangeDutyCycle(duty)     #デューティ比を変更
#######################################
# 直進処理
#######################################
def functionStraight():
    global STARTUP_DONE
    if STARTUP_DONE == True:
        print("functionStraight")
        servo_angle(20)
    
#######################################
# 右旋回処理
#####################################d##
def functionRightTurn():
    global STARTUP_DONE
    if STARTUP_DONE == True:
        print("functionRightTurn")
        servo_angle(50)

#######################################
# 左旋回処理
######################################d#
def functionLeftTurn():
    global STARTUP_DONE
    if STARTUP_DONE == True:
        print("functionLeftTurn")
        servo_angle(-30)

#######################################
# カメラ起動処理
#######################################
def functionStartCamera():
    print("functionStartCamera")
    
    args = shlex.split(MOMO_COMMAND)
    ret = subprocess.Popen(args)
    
    print(ret)

#######################################
# カメラ終了処理
#######################################
def functionStopCamera():
    print("functionStopCamera")

#######################################
# 起動時処理
#######################################
def init():
    # AWS IoT Connect Info
    global MQTT_CLIENT
    MQTT_CLIENT = AWSIoTMQTTClient(MQTT_CLIENT)
    MQTT_CLIENT.configureEndpoint(ENDPOINT_URL, ENDPOINT_PORT)
    MQTT_CLIENT.configureCredentials(ROOT_CA_PATH, PRIVATE_KEY_PATH, PRIVATE_CERT_PATH)

    # AWS IoT Connect Setting
    MQTT_CLIENT.configureOfflinePublishQueueing(-1)
    MQTT_CLIENT.configureDrainingFrequency(2)
    MQTT_CLIENT.configureConnectDisconnectTimeout(10)
    MQTT_CLIENT.configureMQTTOperationTimeout(5)

    MQTT_CLIENT.connect()

###########################################
# subscribeCallback
###########################################
def subscribeCallback(client, userdata, message):
    print('Received a new message')
    print(message.payload)
    payload = json.loads(message.payload)

    action = payload['action']
    direction = payload['direction']

    if action == STARTUP_COMMAND:
        ## 起動処理
        functionStartUp()
    elif action == CAMERA_ON_COMMAND:
        ## カメラ起動処理
        functionStartCamera()
    elif action == CAMERA_OFF_COMMAND:
        ## カメラ終了処理
        functionStopCamera()
    elif action == MOVE_COMMAND:
        ## 直進処理
        functionDrive()
    elif action == STOP_COMMAND:
        ## 停止処理
        functionSuspension()
    elif action == BACK_COMMAND:
        ## 後退処理
        functionBack()
    elif action == END_COMMAND:
        ##  終了処理
        funcitonEnd()

    if direction == STRAIGHT_COMMAND:
        ## 直進処理
        functionStraight()
    elif direction == LEFT_COMMAND:
        ## 左旋回処理
        functionLeftTurn()
    elif direction == RIGHT_COMMAND:
        ## 右旋回処理
        functionRightTurn()

###########################################
# メイン処理
###########################################
def main():
    init()

    try:
        while True:
            MQTT_CLIENT.subscribe(TOPIC_NAME, 1, subscribeCallback)
            time.sleep(1)

    finally:
        funcitonEnd()
        GPIO.cleanup()
        
if __name__ == "__main__":
    sys.exit(main())