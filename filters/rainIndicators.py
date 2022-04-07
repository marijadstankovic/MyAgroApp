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

rawThings = requests.get(url = host + port + "/things?name=rain-indicators",
                headers = headers)
                
print(rawThings)
thing = json.loads(rawThings.text)['things'][0]
print(thing)

rawChannels = requests.get(url = host + port + "/things/" + thing['id'] + "/channels",
                headers = headers)
                
print(rawChannels)
channels = json.loads(rawChannels.text)['channels']
print(channels)

alert_channel = json.loads(requests.get(url = host + port + "/channels?name=alert",
                headers = headers).text)['channels'][0]

airQueue = []
soilQueue = []

def checkIfItRains():
    if(len(airQueue) > 3 and len(soilQueue) > 3):
        # calculate average and send with coordinates
        # or without average
        message = json.dumps(
        [{"bn": "rain",
        "n": "alert",
        "u": "uni",
        "v": 2# int(value)
        }])
        #salji sve poruke?
        print("It's raining")
        client.publish(
            "channels/"+alert_channel['id']+"/messages/freeze",
            payload=message)

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(air_moisture_subtopic)
    client.subscribe(soil_moist_subtopic)

def on_message(client, userdata, msg):
    print('wrong message')
    print(msg.topic+" "+str(msg.payload))
    
def on_air_moisture(client, userdata, msg):
    print('on on_air_moisture message')
    message = json.loads(msg.payload)
    print(msg.topic)
    print(message)
    if(message[0]['v'] >= int(configs['air_moisture'])):
        airQueue.append(message)
    
def on_soil_moist(client, userdata, msg):
    print('on on_soil_moist message')
    message = json.loads(msg.payload)
    print(msg.topic)
    print(message)
    if(message[0]['v'] >= int(configs['soil_moisture'])):
        soilQueue.append(message)
    
    
client = mqtt.Client("rainIndicators")
client.on_connect = on_connect
client.on_message = on_message


air_moisture_channel = [ch for ch in channels if ch['name'] == "air-moisture"][0]
air_moisture_subtopic = "channels/"+air_moisture_channel['id']+"/messages"
print(air_moisture_subtopic)
client.message_callback_add(air_moisture_subtopic,on_air_moisture)

soil_moist_channel = [ch for ch in channels if ch['name'] == "soil-moisture"][0]
soil_moist_subtopic = "channels/"+soil_moist_channel['id']+"/messages"
print(soil_moist_subtopic)
client.message_callback_add(soil_moist_subtopic,on_soil_moist)

client.username_pw_set(thing['id'], thing['key'])
client.connect("192.168.0.101")

client.loop_forever()
