import requests
import json
import paho.mqtt.client as mqtt
import configparser

config_temp = configparser.RawConfigParser()
config_temp.read('sensor_config.cfg')
configs = dict(config_temp.items('SPRINKLER'))
print(configs)

host="http://192.168.0.101" #raspberry2
port=":8182"
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2MzY2Njk1NjksImlhdCI6MTYzNjYzMzU2OSwiaXNzIjoibWFpbmZsdXguYXV0aCIsInN1YiI6Im1hcmlqYS5kLnN0YW5rb3ZpY0BlbGZhay5ycyIsImlzc3Vlcl9pZCI6IjM2MmY3MDUxLWEzNzctNDBiYS1hMjFlLTAwZTIzNzVjYzdhZSIsInR5cGUiOjB9.jewXFzrdyTMFJ7MuPRjaT--kf1wTYd2XwuXSo5F-iDQ"


headers = {
    "Content-Type": "application/json",
    "Authorization": token
}

rawThings = requests.get(url = host + port + "/things?name=soil-pH-actuator",
                headers = headers)
                
print(rawThings)
thing = json.loads(rawThings.text)['things'][0]
print(thing)

rawChannels = requests.get(url = host + port + "/things/" + thing['id'] + "/channels",
                headers = headers)
                
print(rawChannels)
channel = json.loads(rawChannels.text)['channels'][0]
print(channel)

commands_channel = json.loads(requests.get(url = host + port + "/channels?name=commands",
                headers = headers).text)['channels'][0]
alert_channel = json.loads(requests.get(url = host + port + "/channels?name=alert",
                headers = headers).text)['channels'][0]
                
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(subtopic)

def on_message(client, userdata, msg):
    print('wrong message')
    print(msg.topic+" "+str(msg.payload))
    
def on_soil_ph(client, userdata, msg):
    print('on spec message')
    message = json.loads(msg.payload)
    print(msg.topic)
    print(message)
    if(message[0]['v'] < int(configs['high_acid'])):
        print("fertilizer ammoniumN")
        message = json.dumps(
            [{"bn": "fertilizer",
            "n": "command",
            "u": "uni",
            "v": 2# int(value)
            }])
        #salji sto je ukljucena prskalica
        client.publish(
            "channels/"+commands_channel['id']+"/messages/sprinkler",
            payload=message)
    if(message[0]['v'] < int(configs['high_alcaly'])):
        print("fertilizer ammoniumN")
        message = json.dumps(
            [{"bn": "f",
            "n": "alert",
            "u": "uni",
            "v": 2# int(value)
            }])
        client.publish(
            "channels/"+alert_channel['id']+"/messages/ph",
            payload=message)
    
    
    
client = mqtt.Client("soilpHactuator")
client.on_connect = on_connect
client.on_message = on_message


subtopic = "channels/"+channel['id']+"/messages"
print(subtopic)
client.message_callback_add(subtopic,on_soil_ph)

client.username_pw_set(thing['id'], thing['key'])
client.connect("192.168.0.101")

client.loop_forever()
