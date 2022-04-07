import requests
import json

host="http://192.168.0.101" #raspberry2
port=":8182"
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2MzY2Njk1NjksImlhdCI6MTYzNjYzMzU2OSwiaXNzIjoibWFpbmZsdXguYXV0aCIsInN1YiI6Im1hcmlqYS5kLnN0YW5rb3ZpY0BlbGZhay5ycyIsImlzc3Vlcl9pZCI6IjM2MmY3MDUxLWEzNzctNDBiYS1hMjFlLTAwZTIzNzVjYzdhZSIsInR5cGUiOjB9.jewXFzrdyTMFJ7MuPRjaT--kf1wTYd2XwuXSo5F-iDQ"

headers = {
    "Content-Type": "application/json",
    "Authorization": token
}

filters = [{"name": "air-temperature-filter"}, {"name": "air-moisture-filter"}, {"name": "soil-temperature-filter"}, {"name": "soil-moisture-filter"}, {"name": "soil-pH-filter"}, {"name": "daily-filter"}]

rawThings = requests.post(url = host + port + "/things/bulk",
                json = filters,
                headers = headers)

print(rawThings)
filters = json.loads(rawThings.text)['things']
print(filters)

export_channels = [{"name": "daily-export"}, {"name": "not-average-export"}]
rawChannels = requests.post(url = host + port + "/channels/bulk",
                json = export_channels,
                headers = headers)


rawChannels = requests.get(url = host + port + "/channels",
                headers = headers)

print(rawChannels)
channels = json.loads(rawChannels.text)['channels']
print(channels)


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
    

#channels = [{"name": "air-temp"}, {"name": "air-moisture"}, {"name": "soil-temperature"}, {"name": "soil-moisture"}, {"name": "soil-pH"}]

daily_filter = [th['id'] for th in filters if th['name'] == "daily-filter"]
connect_thing_channel(daily_filter, [ch['id'] for ch in channels])

not_avg_filters = [th['id'] for th in filters if th['name'] != "daily-filter"]
not_avg_exp_channel = [ch['id'] for ch in channels if ch['name'] == "not-average-export"]
connect_thing_channel(not_avg_filters, not_avg_exp_channel)



connect_thing_channel([th['id'] for th in filters if th['name'] == "air-temperature-filter"],
                        [ch['id'] for ch in channels if ch['name'] == "air-temperature"])

connect_thing_channel([th['id'] for th in filters if th['name'] == "air-moisture-filter"],
                        [ch['id'] for ch in channels if ch['name'] == "air-moisture"])
                        
connect_thing_channel([th['id'] for th in filters if th['name'] == "soil-temperature-filter"],
                        [ch['id'] for ch in channels if ch['name'] == "soil-temperature"])

connect_thing_channel([th['id'] for th in filters if th['name'] == "soil-moisture-filter"],
                        [ch['id'] for ch in channels if ch['name'] == "soil-moisture"])

connect_thing_channel([th['id'] for th in filters if th['name'] == "soil-pH-filter"],
                        [ch['id'] for ch in channels if ch['name'] == "soil-pH"])




#sprinkler = [th for th in things if th['name'] == "sprinkler"][0]

#sprChs = [ch for ch in channels if ch['name'] == "air-temp" or ch['name'] == "soil-moisture"]

#connect_thing_channel([sprinkler['id']], [ch['id'] for ch in sprChs])

#freezeAlert = [th for th in things if th['name'] == "freeze-alert"][0]
#frzChs = [ch for ch in channels if ch['name'] == "soil-temperature"][0]
#connect_thing_channel([freezeAlert['id']], [frzChs['id']])

#rainIndicators = [th for th in things if th['name'] == "rain-indicators"][0]
#rainChs = [ch for ch in channels if ch['name'] == "air-moisture" or ch['name'] == "soil-moisture"]
#connect_thing_channel([rainIndicators['id']], [ch['id'] for ch in rainChs])

#soilPHActuator = [th for th in things if th['name'] == "soil-pH-actuator"][0]
#soilPhChs = [ch for ch in channels if ch['name'] == "soil-pH"][0]
#connect_thing_channel([soilPHActuator['id']], [soilPhChs['id']])


    
    
    
    
    