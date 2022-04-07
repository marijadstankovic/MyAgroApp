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

rawThings = requests.get(url = host + port + "/things?name=sprinkler",
                headers = headers)
                
print(rawThings)
thing = json.loads(rawThings.text)['things'][0]
print(thing)

rawChannels = requests.get(url = host + port + "/things/" + thing['id'] + "/channels",
                headers = headers)
                
print(rawChannels)
channels = json.loads(rawChannels.text)['channels']
print(channels)

commands_channel = json.loads(requests.get(url = host + port + "/channels?name=commands",
                headers = headers).text)['channels'][0]

highTempFlag = False;
lowSoilMoistFlag = False;
def activateSprinkler():
    if(highTempFlag and lowSoilMoistFlag):
        print("prskalica")
        message = json.dumps(
            [{"bn": "sprinkler",
            "n": "command",
            "u": "uni",
            "v": 2# int(value)
            },
            tempLastValue,
            soilLastValue])
        #salji sto je ukljucena prskalica
        print(message)
        client.publish(
            "channels/"+commands_channel['id']+"/messages/sprinkler",
            payload=message)

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(air_temp_subtopic)
    client.subscribe(soil_moist_subtopic)

def on_message(client, userdata, msg):
    print('wrong message')
    print(msg.topic+" "+str(msg.payload))
    
def on_air_temp(client, userdata, msg):
    print('on air message')
    message = json.loads(msg.payload)
    print(msg.topic)
    print(message)
    global highTempFlag
    if(message[0]['v'] > int(configs['high_air_temp'])):
        highTempFlag = True
        global tempLastValue
        tempLastValue = message
    else:
        highTempFlag = False
    activateSprinkler()
    
def on_soil_moist(client, userdata, msg):
    print('on soil message')
    message = json.loads(msg.payload)
    print(msg.topic)
    print(message)
    global lowSoilMoistFlag
    if(message[0]['v'] < int(configs['low_soil_moist'])):
        lowSoilMoistFlag = True
        global soilLastValue
        soilLastValue = message
    else:
        lowSoilMoistFlag = False
    activateSprinkler()
    
client = mqtt.Client("sprinkler")
client.on_connect = on_connect
client.on_message = on_message


air_temp_channel = [ch for ch in channels if ch['name'] == "air-temp"][0]
air_temp_subtopic = "channels/"+air_temp_channel['id']+"/messages"
print(air_temp_subtopic)
client.message_callback_add(air_temp_subtopic,on_air_temp)

soil_moist_channel = [ch for ch in channels if ch['name'] == "soil-moisture"][0]
soil_moist_subtopic = "channels/"+soil_moist_channel['id']+"/messages"
print(soil_moist_subtopic)
client.message_callback_add(soil_moist_subtopic,on_soil_moist)

client.username_pw_set(thing['id'], thing['key'])
client.connect("192.168.0.101")

client.loop_forever()
