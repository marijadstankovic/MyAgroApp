import requests
import json
import paho.mqtt.client as mqtt
import configparser

config_temp = configparser.RawConfigParser()
config_temp.read('sensor_config.cfg')
configs = dict(config_temp.items('FREEZE_ALERT'))
print(configs)

host="http://192.168.0.101" #raspberry2
port=":8182"
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2MzY2Njk1NjksImlhdCI6MTYzNjYzMzU2OSwiaXNzIjoibWFpbmZsdXguYXV0aCIsInN1YiI6Im1hcmlqYS5kLnN0YW5rb3ZpY0BlbGZhay5ycyIsImlzc3Vlcl9pZCI6IjM2MmY3MDUxLWEzNzctNDBiYS1hMjFlLTAwZTIzNzVjYzdhZSIsInR5cGUiOjB9.jewXFzrdyTMFJ7MuPRjaT--kf1wTYd2XwuXSo5F-iDQ"


headers = {
    "Content-Type": "application/json",
    "Authorization": token
}

rawThings = requests.get(url = host + port + "/things?name=freeze-alert",
                headers = headers)
                
print(rawThings)
thing = json.loads(rawThings.text)['things'][0]
print(thing)

rawChannels = requests.get(url = host + port + "/things/" + thing['id'] + "/channels",
                headers = headers)
                
print(rawChannels)
channel = json.loads(rawChannels.text)['channels'][0]
print(channel)

alert_channel = json.loads(requests.get(url = host + port + "/channels?name=alert",
                headers = headers).text)['channels'][0]
   
def send_message():
    message = json.dumps(
        [{"bn": "soilFreeze",
        "n": "alert",
        "u": "uni",
        "v": 2# int(value)
        }])
    #salji sto je ukljucena prskalica
    print("freezing")
    client.publish(
        "channels/"+alert_channel['id']+"/messages/freeze",
        payload=message)

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(subtopic)

def on_message(client, userdata, msg):
    print('on message')
    print(msg.topic+" "+str(msg.payload))
    
def on_soil_temp(client, userdata, msg):
    print('on spec message')
    message = json.loads(msg.payload)
    print(msg.topic)
    print(message)
    if(message[0]['v'] <= int(configs['low_soil_temperature'])):# and not message_sent):
        send_message()
        #global message_sent = true
    
    
    
client = mqtt.Client("freezeAlert")
client.on_connect = on_connect
client.on_message = on_message

subtopic = "channels/"+channel['id']+"/messages"
print(subtopic)
client.message_callback_add(subtopic,on_soil_temp)

client.username_pw_set(thing['id'], thing['key'])
client.connect("192.168.0.101")

client.loop_forever()
