import requests
import json

host="http://192.168.0.101" #raspberry2
port=":8182"
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2MzY2Njk1NjksImlhdCI6MTYzNjYzMzU2OSwiaXNzIjoibWFpbmZsdXguYXV0aCIsInN1YiI6Im1hcmlqYS5kLnN0YW5rb3ZpY0BlbGZhay5ycyIsImlzc3Vlcl9pZCI6IjM2MmY3MDUxLWEzNzctNDBiYS1hMjFlLTAwZTIzNzVjYzdhZSIsInR5cGUiOjB9.jewXFzrdyTMFJ7MuPRjaT--kf1wTYd2XwuXSo5F-iDQ"

headers = {
    "Content-Type": "application/json",
    "Authorization": token
}

actuators = [{"name": "sprinkler"}, {"name": "freeze-alert"}, {"name": "rain-indicators"}, {"name": "soil-pH-actuator"}]

rawThings = requests.post(url = host + port + "/things/bulk",
                json = actuators,
                headers = headers)

print(rawThings)
things = json.loads(rawThings.text)['things']
print(things)

rawChannels = requests.get(url = host + port + "/channels",
                headers = headers)
                
print(rawChannels)
channels = json.loads(rawChannels.text)['channels']
print(channels)

channelsForCloud = [{"name":"daily"}, {"name": "commands"}, {"name":"alert"}]
rawChannelsForCloud = requests.post(url = host + port + "/channels/bulk",
                json = channelsForCloud,
                headers = headers)
channelsForCloud = json.loads(rawChannelsForCloud.text)['channels']




def connect_thing_channel(thing_ids, channel_ids):
    json = {
    "thing_ids": thing_ids,
    "channel_ids": channel_ids
    }
    print(json)
    q = requests.post(url = host + port + "/connect",
                    json = json,
                    headers = {"Authorization":token})
    print(q)
    
connect_thing_channel([th['id'] for th in things], [ch['id'] for ch in channelsForCloud])
#channels = [{"name": "air-temp"}, {"name": "air-moisture"}, {"name": "soil-temperature"}, {"name": "soil-moisture"}, {"name": "soil-pH"}]

sprinkler = [th for th in things if th['name'] == "sprinkler"][0]
sprChs = [ch for ch in channels if ch['name'] == "air-temp" or ch['name'] == "soil-moisture"]
connect_thing_channel([sprinkler['id']], [ch['id'] for ch in sprChs])

freezeAlert = [th for th in things if th['name'] == "freeze-alert"][0]
frzChs = [ch for ch in channels if ch['name'] == "soil-temperature"][0]
connect_thing_channel([freezeAlert['id']], [frzChs['id']])

rainIndicators = [th for th in things if th['name'] == "rain-indicators"][0]
rainChs = [ch for ch in channels if ch['name'] == "air-moisture" or ch['name'] == "soil-moisture"]
connect_thing_channel([rainIndicators['id']], [ch['id'] for ch in rainChs])

soilPHActuator = [th for th in things if th['name'] == "soil-pH-actuator"][0]
soilPhChs = [ch for ch in channels if ch['name'] == "soil-pH"][0]
connect_thing_channel([soilPHActuator['id']], [soilPhChs['id']])


    
    
    
    
    