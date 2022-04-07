import requests
import json

host="http://192.168.0.101" #raspberry2
port=":8182"
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2MzY2Njk1NjksImlhdCI6MTYzNjYzMzU2OSwiaXNzIjoibWFpbmZsdXguYXV0aCIsInN1YiI6Im1hcmlqYS5kLnN0YW5rb3ZpY0BlbGZhay5ycyIsImlzc3Vlcl9pZCI6IjM2MmY3MDUxLWEzNzctNDBiYS1hMjFlLTAwZTIzNzVjYzdhZSIsInR5cGUiOjB9.jewXFzrdyTMFJ7MuPRjaT--kf1wTYd2XwuXSo5F-iDQ"

sensors = []

for i in range(1, 30):
    sensors.append({"name": "sensor-" + str(i)})
    
print(sensors)

headers = {
    "Content-Type": "application/json",
    "Authorization": token
}

rawThings = requests.post(url = host + port + "/things/bulk",
                json = sensors,
                headers = headers)
                
print(rawThings)
things = json.loads(rawThings.text)['things']
print(things)

#created_at,entry_id,ambient air temp,ambient air moisture,soil temperature,soil moisture,soil pH,latitude,longitude,elevation,status
channels = [{"name": "air-temp"}, {"name": "air-moisture"}, {"name": "soil-temperature"}, {"name": "soil-moisture"}, {"name": "soil-pH"}]

rawChannels = requests.post(url = host + port + "/channels/bulk",
                json = channels,
                headers = headers)
                
print(rawChannels)
channels = json.loads(rawChannels.text)['channels']
print(channels)

json = {
"thing_ids": [th['id'] for th in things],
"channel_ids": [ch['id'] for ch in channels]
}
print(json)
q = requests.post(url = host + port + "/connect",
                json = json,
                headers = {"Authorization":token})
print(q)
