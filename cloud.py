import requests
import json
import paho.mqtt.client as mqtt


resp = requests.get("http://localhost:8202/things/bootstrap/pi2",
            headers={"Authorization":"raspberry2"})
thing = json.loads(resp.text)

channels = thing['mainflux_channels']
control_channel = list(filter(lambda x : x['name'] == 'control-channel', channels))[0]
data_channel = list(filter(lambda x : x['name'] == 'data-channel', channels))[0]
	
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("channels/"+data_channel['id']+"/messages/#")
    
    #channels/6d9c5b01-d5a5-45a2-bc69-e89035e3bf26/messages/res/#

def on_message(client, userdata, msg):
    print('on message')
    print(msg.topic+" "+str(msg.payload))
    
def on_spec_message(client, userdata, msg):
    print('on spec message')
    message = json.loads(msg.payload)
    print(msg.topic)
    print(message)
    command = json.dumps([{"bn":"1", "n":"my_custom_service", "vs":"add_command"}])
    client.publish(
    "channels/"+control_channel["id"]+"/messages/services/service_name/subtopic",
    payload = command
    )
    
    
    
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

subtopic = "channels/"+data_channel['id']+"/messages/channels/+/test"
print(subtopic)
client.message_callback_add(subtopic,on_spec_message)

client.username_pw_set(thing['mainflux_id'], thing['mainflux_key'])
client.connect("192.168.0.100")

client.loop_forever()