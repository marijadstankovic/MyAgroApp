# MyAgroApp

The application uses sensors for air humidity, air temperature, soil moisture, soil temperature and soil acidity.

The application modeled on the standard IoT architecture has an edge and a cloud layer. In the edge layer, the main component is represented by the Mainflux edge version, which collects data from the sensors, delivers them to other components that need them and stores them in the database, together with the basic information about the sensors. It also enables communication with the server. Sensors are components that represent sensor nodes in the real world, and they simply send readings to different channels. Filters are components for processing and sending data to the server. Actuators receive commands from the server and react accordingly – turning sprinklers/fermenter on or off. Figure 1 shows the edge layer with Mainflux and additional components. The cloud layer represents a server on which filtered data from edge devices is collected. It stores data about users, their entities and connections, as well as messages. Figure 2 shows the cloud layer and how the edge device is connected to it. One edge device is represented by one thing entity. It sends data to the data channel and receives commands from the control channel. The data processing unit listens to messages from the data channel and accordingly issues commands to the control channel. Figure 3 shows the entire system architecture.

Figure 1:
---

![EDGE](https://user-images.githubusercontent.com/58818571/185634638-0e6847a1-bdde-4f0d-a549-3a98a2e46d71.png)




Figure 2:
---

![CLOUD](https://user-images.githubusercontent.com/58818571/185634756-64af7965-ecae-4ad1-b4ac-43707cbe7c6a.png)



Figure 3:
-----
![Mainflux](https://user-images.githubusercontent.com/58818571/185634884-18096ffa-6435-4807-9dd8-84d87df8bcf5.png)
