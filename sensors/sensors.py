import requests
import json
import paho.mqtt.client as mqtt
from os.path import dirname, join
import csv
import time
import datetime

file = "data.csv"

host="http://192.168.0.101"
port=":8182"
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2MzY2Njk1NjksImlhdCI6MTYzNjYzMzU2OSwiaXNzIjoibWFpbmZsdXguYXV0aCIsInN1YiI6Im1hcmlqYS5kLnN0YW5rb3ZpY0BlbGZhay5ycyIsImlzc3Vlcl9pZCI6IjM2MmY3MDUxLWEzNzctNDBiYS1hMjFlLTAwZTIzNzVjYzdhZSIsInR5cGUiOjB9.jewXFzrdyTMFJ7MuPRjaT--kf1wTYd2XwuXSo5F-iDQ"

headers={"Authorization":token}
rawThings = requests.get(url = host + port + "/things?name=sensor&limit=30", #?name=sensor&limit=30
                        headers = headers)
things = json.loads(rawThings.text)['things']
print (things[0])
rawChannels = requests.get(url = host + port + "/channels",
                        headers = headers)
channels = json.loads(rawChannels.text)['channels']
print(channels[0])
#print(things)
#print(channels)
#otprilike 6ha, 2.22 * 2.28
sensor_coordinates = [
[43.220350198, 22.007748779],
[43.220029644, 22.008188662],
[43.219630903, 22.008671459],
[43.219294708, 22.009229359],
[43.218919419, 22.009765800],
[43.220334561, 22.006997761],
[43.220068736, 22.007341084],
[43.219740362, 22.007759508],
[43.219357256, 22.008242306],
[43.218958511, 22.008746561],
[43.218551945, 22.009283003],
[43.220131283, 22.006289658],
[43.219716906, 22.006826099],
[43.219365075, 22.007255253],
[43.219021060, 22.007705864],
[43.218606675, 22.008220848],
[43.220029644, 22.005442080],
[43.219795091, 22.005753216],
[43.219365075, 22.006289658],
[43.219005423, 22.006750998],
[43.218168832, 22.007587847],
[43.217918635, 22.007877525],
[43.218489396, 22.006944117],
[43.218739591, 22.006375488],
[43.218950693, 22.005785402],
[43.219435441, 22.005238232],
[43.219232160, 22.004916367],
[43.219716906, 22.004873451],
[43.219388530, 22.004379925]
]

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

clients = []
for thing in things:
    client = mqtt.Client(thing['name'])
    client.on_connect = on_connect
    client.username_pw_set(thing['id'], thing['key'])
    client.connect("192.168.0.101")
    clients.append(client)
print(clients)

def send_data(unit, value, time, channel, thing_index):
    message = json.dumps(
            [{"bn": "s:" + str(thing_index),
            "bt": time,
            "n": channel["name"],
            "u": unit,
            "v": int(value)
            },
            # {
            # #"n": "lat",
            # "u": "lat",
            # "vs": str(sensor_coordinates[index][0])
            # },
            # {
            # #"n": "lon",
            # "u": "lon",
            # "vs": str(sensor_coordinates[index][1])
            # }
            ])
    #print(clients[thing_index])
    print(channel['id'])
    print(message)
    clients[thing_index].publish(
        "channels/"+channel['id']+"/messages",
        payload=message)

with open(join(dirname(__file__),file), 'r', encoding="utf8") as db:
    reader = csv.reader(db)
    next(reader) #skip the header
    index=0
    for row in reader:
        print(row)
        datetimeobj=datetime.datetime.strptime(row[0][:19], "%Y-%m-%d %H:%M:%S")
        timestamp = datetimeobj.timestamp()
        for channel in channels:
        # "air-temp"}, {"name": "air-moisture"}, {"name": "soil-temperature"}, {"name": "soil-moisture"}, {"name": "soil-pH"
        
        #0 created_at,1 entry_id,2 ambient air temp,3 ambient air moisture,4 soil temperature,5 soil moisture,6 soil pH,7 latitude,8 longitude,9 elevation,10 status
            if(channel["name"] == "air-temperature"):
                send_data("Cel", row[2], timestamp, channel, index)
                
            elif(channel["name"] == "air-moisture"):
                send_data("%RH", row[3], timestamp, channel, index)
                
            elif(channel["name"] == "soil-temperature"):
                send_data("Cel", row[4], timestamp, channel, index)
                
            elif(channel["name"] == "soil-moisture"):
                send_data("%RH", row[5], timestamp, channel, index)
                
            elif(channel["name"] == "soil-pH"):
                send_data("pH", row[6], timestamp, channel, index)
        time.sleep(6)        
        index = index + 1
        if index > len(things) - 1:
            index = 0
            #time.sleep(10)
        
        
        
        
        
        
        
        
        
        
        
        