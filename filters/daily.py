import requests
import json
import paho.mqtt.client as mqtt
import configparser

def average_data(message):
    print(message)
    # messages[message[0]['bn']] = message
    if message[0]['bn'] not in messages:
        messages[message[0]['bn']] = message
    else:
        average()
    print(len(messages))
#    client.publish(
 #       "channels/"+export_channel['id']+"/messages/air-temperature",
  #      payload=message)

def average():
    print("average")
    print(messages['sensor 1'][0]['v'])
    value = sum( int(msg[0]['v']) for msg in messages.values()) / len(messages)
    print(value)
    message = json.dumps(
    [{
    "u": "degree celsius",
    "v": value
    }])
    print(message)
    client.publish(
        "channels/"+export_channel['id']+"/messages/air-temperature",
        payload=message)
    messages.clear()
    client.unsubscribe(air_temp_subtopic)
    client.disconnect()

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    print(air_temp_subtopic)
    client.subscribe(air_temp_subtopic)

def on_message(client, userdata, msg):
    print('wrong message')
    print(msg.topic+" "+str(msg.payload))
    
def on_air_temp(client, userdata, msg):
    print('on air message')
    message = json.loads(msg.payload)
    print(msg.topic)
    print(message)
    average_data(message)
    
def main():

    host="http://192.168.0.101" #raspberry2
    port=":8182"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2MzY2Njk1NjksImlhdCI6MTYzNjYzMzU2OSwiaXNzIjoibWFpbmZsdXguYXV0aCIsInN1YiI6Im1hcmlqYS5kLnN0YW5rb3ZpY0BlbGZhay5ycyIsImlzc3Vlcl9pZCI6IjM2MmY3MDUxLWEzNzctNDBiYS1hMjFlLTAwZTIzNzVjYzdhZSIsInR5cGUiOjB9.jewXFzrdyTMFJ7MuPRjaT--kf1wTYd2XwuXSo5F-iDQ"


    headers = {
        "Content-Type": "application/json",
        "Authorization": token
    }

    rawThings = requests.get(url = host + port + "/things?name=daily-filter",
                    headers = headers)
                    
    thing = json.loads(rawThings.text)['things'][0]

    rawChannels = requests.get(url = host + port + "/things/" + thing['id'] + "/channels",
                    headers = headers)
                    
    channels = json.loads(rawChannels.text)['channels']
    print(channels)

    global air_temp_channel
    air_temp_channel = [ch for ch in channels if ch['name'] == "air-temperature"][0]
    
    global export_channel
    export_channel = [ch for ch in channels if ch['name'] == "daily-export"][0]

    global air_temp_subtopic
    air_temp_subtopic = "channels/"+air_temp_channel['id']+"/messages"

    global messages
    messages = {}

    global client
    client = mqtt.Client("air-temp-filter")
    client.on_connect = on_connect
    client.on_message = on_message

    client.message_callback_add(air_temp_subtopic,on_air_temp)


    client.username_pw_set(thing['id'], thing['key'])
    client.connect("192.168.0.101")

    client.loop_forever()
