import asyncio
#pyp install nats-py
from nats.aio.client import Client as NATS
import json

async def run(loop):
    nc = NATS()

    async def disconnected_cb():
        print("Got disconnected...")

    async def reconnected_cb():
        print("Got reconnected...")

    await nc.connect("192.168.0.101",
                     reconnected_cb=reconnected_cb,
                     disconnected_cb=disconnected_cb,
                     max_reconnect_attempts=-1)
                     #loop=loop)

    async def fermenter_on(msg):
        subject = msg.subject
        reply = msg.reply
        data = json.loads(msg.data.decode())
        print("Received a message on '{subject}': {data}".format(
            subject=subject, data=data))
        #print("Sprinkler on, location: {lat}, {lon}".format(lat=data[1]['sv'], lon=data[2]['sv']))
        #await nc.publish(reply, b'I can help')

    # Use queue named 'workers' for distributing requests
    # among subscribers.
    await nc.subscribe("commands.fermenter", "workers", fermenter_on) #, "workers"

    print("Listening for requests on 'fermentizer' subject...")
    for i in range(1, 1000000):
        await asyncio.sleep(1)
        #try:
         #   response = await nc.request("commands.service_name.subtopic", b'hi')
          #  print(response)
        #except Exception as e:
           # print("Error:", e)

loop = asyncio.get_event_loop()
loop.run_until_complete(run(loop))
loop.run_forever()
loop.close()