import requests
import json
import paho.mqtt.client as mqtt
import configparser

config_temp = configparser.RawConfigParser()
config_temp.read('filter_config.cfg')
configs = dict(config_temp.items('AIR_MOISTURE'))
print(configs)
high_air_moist = int(configs['high'])

host="http://192.168.0.101" #raspberry2
port=":8182"
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2MzY2Njk1NjksImlhdCI6MTYzNjYzMzU2OSwiaXNzIjoibWFpbmZsdXguYXV0aCIsInN1YiI6Im1hcmlqYS5kLnN0YW5rb3ZpY0BlbGZhay5ycyIsImlzc3Vlcl9pZCI6IjM2MmY3MDUxLWEzNzctNDBiYS1hMjFlLTAwZTIzNzVjYzdhZSIsInR5cGUiOjB9.jewXFzrdyTMFJ7MuPRjaT--kf1wTYd2XwuXSo5F-iDQ"


headers = {
    "Content-Type": "application/json",
    "Authorization": token
}

rawThings = requests.get(url = host + port + "/things?name=air-moisture-filter",
                headers = headers)
                
print(rawThings)
thing = json.loads(rawThings.text)['things'][0]
print(thing)

rawChannels = requests.get(url = host + port + "/things/" + thing['id'] + "/channels",
                headers = headers)
                
print(rawChannels)
channels = json.loads(rawChannels.text)['channels']
print(channels)

air_moist_channel = [ch for ch in channels if ch['name'] == "air-moisture"][0]
print(air_moist_channel)
export_channel = [ch for ch in channels if ch['name'] == "not-average-export"][0]
print(export_channel)

air_moist_subtopic = "channels/"+air_moist_channel['id']+"/messages"

def publish_data(message):
    print("sending")
    client.publish(
        "channels/"+export_channel['id']+"/messages/air-moisture",
        payload=message)

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(air_moist_subtopic)

def on_message(client, userdata, msg):
    print('wrong message')
    print(msg.topic+" "+str(msg.payload))
    
def on_air_moist_message(client, userdata, msg):
    print('on air moist message')
    message = json.loads(msg.payload)
    print(msg.topic)
    print(message)
    if(message[0]['v'] >= high_air_moist):
        publish_data(msg.payload)
    

client = mqtt.Client("air-moist-filter")
client.on_connect = on_connect
client.on_message = on_message


print(air_moist_subtopic)
client.message_callback_add(air_moist_subtopic,on_air_moist_message)


client.username_pw_set(thing['id'], thing['key'])
client.connect("192.168.0.101")

client.loop_forever()