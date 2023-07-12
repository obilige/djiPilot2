import random
import time

from paho.mqtt import client as mqtt_client


host = 'emqx-broker'
port = 8083
topic = "python/mqtt"
# Generate a Client ID with the subscribe prefix.
client_id = f'subscribe-{random.randint(0, 100)}'
username = 'emqx'
password = 'public'
transport = "websocket"
topic = [('sys/product/+/status', 0), 
         ('sys/product/+/status_reply', 0),
         ('thing/product/#',0) ,]

# test
client = mqtt_client.Client(client_id)
client.connect(host, port)
client.subscribe()
client.publish()
client.disconnect()


class subscribe:
    def __init__(self):
        self.host = host
        self.port = port
        self.topic = topic
        self.client_id = client_id
        self.username = username
        self.password = password
        self.transport = transport
        self.topic = topic


    def client(self) -> mqtt_client:
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)

        client = mqtt_client.Client(client_id = self.client_id, transport = self.transport)
        # client.username_pw_set(username, password)
        client.on_connect = on_connect
        client.connect(host, port)
        return client


    def subscribe(self):
        def on_message(client, userdata, msg):
            print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

        self.client.subscribe(topic)
        self.client.on_message = on_message


    def publish(self, topic, payload):
        msg_count = 1
        while True:
            time.sleep(1)
            result = self.client.publish(topic, payload)
            # result: [0, 1]
            status = result[0]
            if status == 0:
                print(f"Send `{payload}` to topic `{topic}`")
            else:
                print(f"Failed to send message to topic {topic}")
            msg_count += 1
            if msg_count > 5:
                break
 
    
    def disconnet(self, condition):
        if condition:
            self.client.disconnet()
