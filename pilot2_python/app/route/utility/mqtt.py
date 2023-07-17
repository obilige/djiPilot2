import paho.mqtt.client as mqtt

import random
import json
from uuid import uuid4
import datetime
from collections import defaultdict

# config
host = 'emqx-broker'
port = 8083
client_id = f'subscribe-{random.randint(0, 100)}' # Generate a Client ID with the subscribe prefix.
username = 'emqx'
password = 'public'
transport = "websockets"
topic = [('sys/product/+/status', 0), 
         ('sys/product/+/status_reply', 0),
         ('thing/product/#',0) ,]
params = {
    "gatewayList": defaultdict(dict),
    "productList": [
        {"domain": 2, "type": 144, "sub_type": 0, "name": "DJI RC Pro", "node_type": "rc", "explanation": "M3E/M3T, M3M Remote Controller"},
        {"domain": 2, "type": 56, "sub_type": 0, "name": "DJI RC", "node_type": "rc", "explanation": "M300 RTK Remote Controller"},
        {"domain": 0, "type": 77, "sub_type": 2, "name": "Mavic 3M (M3M)", "node_type": "uav", "explanation": ""},
        {"domain": 0, "type": 67, "sub_type": 0, "name": "Matrice 30", "node_type": "uav", "explanation": ""}
    ],
    "deviceList": [
        {"sn": "1581F5FKD232800D2TK8", "domain": 0, "type": 77, "sub_type": 2, "firmware_version": "07.00.0102", "firmware_status": 1, "bound_status": False, "online_status": False},
        {"sn": "5YSZL260021E9E", "domain": 2, "type": 144, "sub_type": 0, "firmware_version": "02.00.0501", "firmware_status": 1, "bound_status": False, "online_status": False, "child_device_sn": "1581F5FKD232800D2TK8"},
        {"sn": "1ZNBJAA0HC0001", "domain": 0, "type": 67, "sub_type": 0, "firmware_version": "02.00.0407", "firmware_status": 1, "bound_status": False, "online_status": False},
        {"sn": "5EKBJ9U001000N", "domain": 2, "type": 56, "sub_type": 0, "firmware_version": "02.00.0407", "firmware_status": 1, "bound_status": False, "online_status": False, "child_device_sn": "1ZNBJAA0HC0001"},
        {"sn": "1ZNBJA90HC002N", "domain": 0, "type": 67, "sub_type": 0, "firmware_version": "02.00.0407", "firmware_status": 1, "bound_status": False, "online_status": False},
        {"sn": "5EKBJ9U001000V", "domain": 2, "type": 56, "sub_type": 0, "firmware_version": "02.00.0407", "firmware_status": 1, "bound_status": False, "online_status": False, "child_device_sn": "1ZNBJA90HC002N"}
    ],
    "topicList": defaultdict(dict)
}


mqtt_client = mqtt.Client(client_id=client_id, transport=transport)
mqtt_client.ws_set_options(path="/mqtt", headers=None)


def on_connect(client, userdata, flags, rc):
    print("[MQTT] connect")
    client.subscribe('sys/product/+/status')
    client.subscribe('sys/product/+/status_reply')
    client.subscribe('thing/product/#')

def on_error(client, userdata, error):
    print("[MQTT-error :", error)

def on_reconnect(client):
    print("[MQTT-reconnect]")

def on_close(client):
    print("[MQTT-close]")

def on_disconnect(client, userdata, rc):
    print("[MQTT-disconnect]")

def on_packetsend(client, packet):
    pass

def on_packetreceive(client, packet):
    pass


def on_message(client, userdata, msg):
    ''' Main Function '''
    pass

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.on_error = on_error
mqtt_client.on_reconnect = on_reconnect
mqtt_client.on_close = on_close
mqtt_client.on_disconnect = on_disconnect
mqtt_client.on_packetsend = on_packetsend
mqtt_client.on_packetreceive = on_packetreceive

mqtt_client.loop_start()