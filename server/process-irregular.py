from datetime import datetime
import requests
import json
import paho.mqtt.client as mqtt
import schedule
import time
import configparser

config_temp = configparser.RawConfigParser()
config_temp.read('threshold_config.cfg')
configs = dict(config_temp.items('THRESHOLD'))
alcaly = int(configs['alcaly'])
acid = int(configs['acid'])
low_soil_moisture = int(configs['low_soil_moisture'])


resp = requests.get("http://localhost:8202/things/bootstrap/external_id126",
            headers={"Authorization":"external_key6"})
thing = json.loads(resp.text)

channels = thing['mainflux_channels']

control_channel = [x for x in channels if x['name'] == 'control-channel'][0]
data_channel = [x for x in channels if x['name'] == 'data-channel'][0]

print(control_channel)
print(data_channel)

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(soil_ph_subtopic)
    client.subscribe(soil_moist_subtopic)
    client.subscribe(soil_temp_subtopic)
    client.subscribe(air_moist_subtopic)
    client.subscribe(air_temp_subtopic)
    #channels/6d9c5b01-d5a5-45a2-bc69-e89035e3bf26/messages/res/#

def on_message(client, userdata, msg):
    print('on message')
    print(msg.topic+" "+str(msg.payload))
    
airTemps = {}
def on_air_temp_message(client, userdata, msg):
    print("data recieved from edge on air temp")
    message = json.loads(msg.payload)
    print(msg.topic)
    print(message)
    airTemps[message[0]['bn']] = message
    play_sprinkler(message[0]['bn'])

airMoists = {}
def on_air_moist_message(client, userdata, msg):
    print("data recieved from edge on air moist")
    message = json.loads(msg.payload)
    print(msg.topic)
    print(message)
    airMoists[message[0]['bn']] = message

soilMoists = {}
def on_soil_moist_message(client, userdata, msg):
    print("data recieved from edge on soil moist")
    message = json.loads(msg.payload)
    print(msg.topic)
    print(message)
    soilMoists[message[0]['bn']] = message
    play_sprinkler(message[0]['bn'])

def on_soil_temp_message(client, userdata, msg):
    print("data recieved from edge on soil temp")
    message = json.loads(msg.payload)

def on_soil_ph_message(client, userdata, msg):
    print("data recieved from edge on soil ph")
    message = json.loads(msg.payload)
    print(msg.topic)
    print(message)
    play_fermenter(message[0]['v'])

def send_command(command, service):
    json_command = json.dumps(
    [{
        "bn":"command",
        "vs":command
    },])
    print(json_command)
    print("channels/"+control_channel["id"]+"/messages/services/"+service)
    client.publish(
        "channels/"+control_channel["id"]+"/messages/services/"+service,
        payload = json_command
    )

sprinkler_is_on = False
sprinkler_time_on = None
def play_sprinkler(key):
    global sprinkler_is_on
    if (
        key not in airTemps
        or
        key not in soilMoists
        or soilMoists[key][0]['v'] > low_soil_moisture): #lower boundary
        return
    #check date time
    global sprinkler_time_on
    sprinkler_time_on = datetime.now()
    if(not sprinkler_is_on):
        sprinkler_is_on = True
        send_command("on", "sprinkler")

fermenter_is_on = False
fermenter_time_on = None
def play_fermenter(value):    
    global fermenter_is_on
    if value <= acid:
        print("Soil too much acid, needs farmer intervantion")
    
    global fermenter_time_on
    if value >= alcaly:
        fermenter_time_on = datetime.now()
        if(not fermenter_is_on):
            send_command("on", "fermenter")
            fermenter_is_on = True
    # else:
    #     if(fermenter_is_on):
    #         # send_command("off", "fermenter")
    #         fermenter_is_on = False

def check_for_off():
    global sprinkler_time_on
    global sprinkler_is_on
    global fermenter_time_on
    global fermenter_is_on
    now = datetime.now()
    if(sprinkler_is_on and sprinkler_time_on != None and (now - sprinkler_time_on).total_seconds() > 6):
        sprinkler_is_on = False
        send_command("off", "sprinkler")

    if(fermenter_is_on and sprinkler_time_on != None and (now - fermenter_time_on).total_seconds() > 6):
        fermenter_is_on = False
        send_command("off", "fermenter")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

#subtopic = "channels/"+data_channel['id']+"/messages/channels/+/test"
base_subtopic = "channels/"+data_channel['id']+"/messages/channels/+/"
air_temp_subtopic = base_subtopic + "air-temperature" #ea823f8c-63c7-41ef-8a70-2a35fc7ffab9"
air_moist_subtopic = base_subtopic + "air-moisture"
soil_temp_subtopic = base_subtopic + "soil-temperature"
soil_moist_subtopic = base_subtopic + "soil-moisture"
soil_ph_subtopic = base_subtopic + "soil-pH"

#subtopic = "channels/200a068e-68a5-4bf8-8f19-5c15590cb4ee/messages/channels/+/air-temperature"
#print(subtopic)
client.message_callback_add(air_temp_subtopic,on_air_temp_message)
client.message_callback_add(air_moist_subtopic,on_air_moist_message)
client.message_callback_add(soil_temp_subtopic,on_soil_temp_message)
client.message_callback_add(soil_moist_subtopic,on_soil_moist_message)
client.message_callback_add(soil_ph_subtopic,on_soil_ph_message)

client.username_pw_set(thing['mainflux_id'], thing['mainflux_key'])
client.connect("192.168.0.100")

#client.loop_forever()
client.loop_start()

def clean_variables():
    print("cleaning")
    airTemps.clear()
    airMoists.clear()
    soilMoists.clear()
    global sprinkler_is_on
    sprinkler_is_on = True
    
schedule.every(3).minutes.do(clean_variables)
schedule.every(1).second.do(check_for_off)
while True :
    schedule.run_pending()
    time.sleep(1)
