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
# DB에 productList, deviceList 정보 등록 후 함수 생성(쿼리 -> config 생성 -> 리턴)
# productList, deviceList 등록하는 기능도 만들어보기
config = {
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




# set mqtt basic function
def on_connect(client, userdata, flags, rc):
    print("[MQTT] connect")
    client.subscribe('sys/product/+/status')
    client.subscribe('sys/product/+/status_reply')
    client.subscribe('thing/product/#')

def on_message(client, userdata, msg):
    topic = msg.topic
    message = msg.payload.decode("utf-8")
    json_data = json.loads(message)

    arr_topic = topic.split("/")
    if arr_topic[0] == "sys" and arr_topic[1] == "product" and arr_topic[3] == "status":
        if topic in config["topicList"]:
            if config["topicList"].get(topic) != json.dumps(json_data):
                config["topicList"].set(topic, json.dumps(json_data))
                print("[MQTT-", topic, "]", "\t", json.dumps(json_data))
        else:
            config["topicList"].set(topic, json.dumps(json_data))
            print("[MQTT-", topic, "]", "\t", json.dumps(json_data))

        gateway_sn = arr_topic[2]
        pObj = next(filter(lambda x: x["domain"] == json_data["data"]["domain"] and x["type"] == json_data["data"]["type"] and x["sub_type"] == json_data["data"]["sub_type"], config["productList"]))
        onlineJSON = {
            "biz_code": "device_online",
            "version": json_data["data"]["version"],
            "timestamp": str(int(datetime.datetime.now().timestamp() * 1000)),
            "data": {
                "sn": gateway_sn,
                "device_model": {"domain": json_data["data"]["domain"], "key": f"{json_data['data']['domain']}-{json_data['data']['type']}-{json_data['data']['sub_type']}", "sub_type": json_data["data"]["sub_type"], "type": json_data["data"]["type"]},
                "online_status": True,
                "device_callsign": pObj["name"],
                "model": pObj["name"],
                "bound_status": True,
                "gateway_sn": "",
                "domain": json_data["data"]["domain"]
            }
        }

        if gateway_sn not in config["gatewayList"]:
            config["deviceList"].find(lambda ele: ele["sn"] == gateway_sn)["bound_status"] = True
            config["deviceList"].find(lambda ele: ele["sn"] == gateway_sn)["online_status"] = True
            print("\t++++ set device_online1", json.dumps(onlineJSON["data"]))
            config["gatewayList"][gateway_sn]["tid"] = json_data["tid"]
            config["gatewayList"][gateway_sn]["bid"] = json_data["bid"]
            config["gatewayList"][gateway_sn]["device_online1"] = onlineJSON
            config["gatewayList"][gateway_sn]["bizCode"] = {"device_online1"}
        else:
            config["gatewayList"][gateway_sn]["tid"] = json_data["tid"]
            config["gatewayList"][gateway_sn]["bid"] = json_data["bid"]

        if len(json_data["data"]["sub_devices"]) > 0:
            if "device_online2" in config["gatewayList"][gateway_sn]:
                config["gatewayList"][gateway_sn]["bizCode"].add("device_online2")
            else:
                subJson = json_data["data"]["sub_devices"][0]
                onlineSubJSON = {
                    "biz_code": "device_online",
                    "version": json_data["data"]["version"],
                    "timestamp": str(int(datetime.datetime.now().timestamp() * 1000)),
                    "data": {
                        "sn": subJson["sn"],
                        "device_model": {"domain": subJson["domain"], "key": f"{subJson['domain']}-{subJson['type']}-{subJson['sub_type']}", "sub_type": subJson["sub_type"], "type": subJson["type"]},
                        "online_status": True,
                        "device_callsign": pObj["name"],
                        "model": pObj["name"],
                        "bound_status": True,
                        "gateway_sn": gateway_sn,
                        "domain": subJson["domain"]
                    }
                }
                config["deviceList"].find(lambda ele: ele["sn"] == subJson["sn"])["bound_status"] = True
                config["deviceList"].find(lambda ele: ele["sn"] == subJson["sn"])["online_status"] = True
                print("\t++++ set device_online2", json.dumps(onlineSubJSON["data"]))
                config["gatewayList"][gateway_sn]["aircraft"] = subJson["sn"]
                config["gatewayList"][gateway_sn]["device_online2"] = onlineSubJSON
                config["gatewayList"][gateway_sn]["bizCode"].add("device_online2")
        elif len(json_data["data"]["sub_devices"]) == 0 and "device_online2" in config["gatewayList"][gateway_sn]:
            onlineSubJSON = config["gatewayList"][gateway_sn]["device_online2"]
            onlineSubJSON["biz_code"] = "device_offline"
            onlineSubJSON["timestamp"] = str(int(datetime.datetime.now().timestamp() * 1000))
            onlineSubJSON["data"]["online_status"] = False
            onlineSubJSON["data"]["bound_status"] = False
            onlineSubJSON["data"]["gateway_sn"] = ""
            print("\t++++ set device_online2", json.dumps(onlineSubJSON["data"]))
            config["gatewayList"][gateway_sn]["device_offline2"] = onlineSubJSON
            del config["gatewayList"][gateway_sn]["device_online2"]
            config["gatewayList"][gateway_sn]["bizCode"].add("device_offline2")
            config["gatewayList"][gateway_sn]["bizCode"].add("device_online1")
            del config["gatewayList"][gateway_sn]["aircraft"]

        MQTT_STATUS_REPLY(arr_topic[2])

    elif arr_topic[0] == "sys" and arr_topic[1] == "product" and arr_topic[3] == "status_reply":
        if topic in config["topicList"]:
            if config["topicList"][topic] != json.dumps(json_data):
                config["topicList"][topic] = json.dumps(json_data)
                print("[MQTT-", topic, "]", "\t", json.dumps(json_data))
        else:
            config["topicList"][topic] = json.dumps(json_data)
            print("[MQTT-", topic, "]", "\t", json.dumps(json_data))

    elif arr_topic[0] == "thing" and arr_topic[1] == "product" and arr_topic[3] == "osd":
        sn = arr_topic[2]
        gateway_sn = json_data["gateway"]
        del json_data["bid"]
        del json_data["tid"]
        if topic in config["topicList"]:
            if config["topicList"][topic] != json.dumps(json_data):
                config["topicList"][topic] = json.dumps(json_data)
                print("[MQTT-", topic, "]", "\t", json.dumps(json_data))
        else:
            config["topicList"].set(topic, json.dumps(json_data))
            print("[MQTT-", topic, "]", "\t", json.dumps(json_data))

        if gateway_sn in config["gatewayList"]:
            if json_data["data"]["live_status"]:
                config["gatewayList"][gateway_sn]["gateway_osd"] = {"biz_code": "gateway_osd", "version": "1.0", "timestamp": str(int(datetime.datetime.now().timestamp() * 1000)), "data": {"host": json_data["data"], "sn": sn}}
                config["gatewayList"][gateway_sn]["bizCode"].add("gateway_osd")
            else:
                config["gatewayList"][gateway_sn]["device_osd"] = {"biz_code": "device_osd", "version": "1.0", "timestamp": str(int(datetime.datetime.now().timestamp() * 1000)), "data": {"host": json_data["data"], "sn": sn}}
                config["gatewayList"][gateway_sn]["bizCode"].add("device_osd")
            config["gatewayList"][gateway_sn]["osd"] = {"biz_code": "device_osd", "version": "1.0", "timestamp": str(int(datetime.datetime.now().timestamp() * 1000)), "data": {"sn": sn}}
            config["gatewayList"][gateway_sn]["bizCode"].add("osd")

    elif arr_topic[0] == "thing" and arr_topic[1] == "product" and arr_topic[3] == "events":
        del json_data["bid"]
        del json_data["tid"]
        if (topic + "|" + json_data["data"]["event"]) in config["topicList"]:
            if config["topicList"][topic + "|" + json_data["data"]["event"]] != json.dumps(json_data):
                config["topicList"][topic + "|" + json_data["data"]["event"]] = json.dumps(json_data)
                print("[MQTT-", topic, "]", "\t", json.dumps(json_data))
        else:
            config["topicList"][topic + "|" + json_data["data"]["event"]] = json.dumps(json_data)
            print("[MQTT-", topic, "]", "\t", json.dumps(json_data))

    elif arr_topic[0] == "thing" and arr_topic[1] == "product" and arr_topic[3] == "state":
        del json_data["bid"]
        del json_data["tid"]
        gateway_sn = arr_topic[2]
        if topic in config["topicList"]:
            if config["topicList"][topic] != json.dumps(json_data):
                config["topicList"][topic] = json.dumps(json_data)
                print("[MQTT-", topic, "]", "\t", json.dumps(json_data))
        else:
            config["topicList"].set(topic, json.dumps(json_data))
            print("[MQTT-", topic, "]", "\t", json.dumps(json_data))

        if "live_capacity" in json_data["data"]:
            if "device_list" in json_data["data"]["live_capacity"]:
                if len(json_data["data"]["live_capacity"]["device_list"]) > 0:
                    config["deviceList"].find(lambda ele: ele["sn"] == gateway_sn)["camera_index"] = json_data["data"]["live_capacity"]["device_list"][0]["camera_list"][0]["camera_index"]
                    config["deviceList"].find(lambda ele: ele["sn"] == gateway_sn)["video_list"] = json_data["data"]["live_capacity"]["device_list"][0]["camera_list"][0]["video_list"]

    else:
        print("======================================[MQTT topic] : ", topic, json.dumps(json_data))


# set client
mqtt_client = mqtt.Client(client_id=client_id, transport=transport)
mqtt_client.ws_set_options(path="/mqtt", headers=None)

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.on_error = lambda client, userdata, msg: print("[MQTT-error : ", msg)
mqtt_client.on_reconnect = lambda: print("[MQTT-reconnect")
mqtt_client.on_close = lambda: print("[MQTT-close")
mqtt_client.on_disconnect = lambda client, userdata, msg: print("[MQTT-disconnect")
mqtt_client.on_offline = lambda: print("[MQTT-offline")
mqtt_client.on_packetsend = lambda client, userdata, msg: None
mqtt_client.on_packetreceive = lambda client, userdata, msg: None


# mqtt function
def MQTT_STATUS_REPLY(gateway_sn):
    mqtt_client.publish('sys/product/' + gateway_sn + '/status_reply', json.dumps({
        "tid": config["gatewayList"][gateway_sn]["tid"],
        "bid": config["gatewayList"][gateway_sn]["bid"],
        "method": "update_topo",
        "data": {"result": 0},
        "timestamp": str(int(datetime.datetime.now().timestamp() * 1000))
    }), qos=0)

def MQTT_LIVE_STOP(params):
    gateway_sn = ""
    arrVideo = params["video_id"].split("/")
    for key, value in config["gatewayList"].items():
        if value["aircraft"] == arrVideo[0]:
            gateway_sn = key
            break
    uuid_tid = str(uuid4())
    uuid_bid = str(uuid4())
    stopJson = {
        "tid": uuid_tid,
        "bid": uuid_bid,
        "method": "live_stop_push",
        "data": {
            "video_id": config["gatewayList"][gateway_sn]["video_id"],
        },
        "timestamp": str(int(datetime.datetime.now().timestamp() * 1000))
    }
    mqtt_client.publish('thing/product/'+gateway_sn+'/services', json.dumps(stopJson), qos=1)

def MQTT_LIVE_START(params):
    gateway_sn = ""
    arrVideo = params["video_id"].split("/")
    for key, value in config["gatewayList"].items():
        if value["aircraft"] == arrVideo[0]:
            gateway_sn = key
            break
    print("[MQTT_LIVE_START] sn", gateway_sn, "params", json.dumps(params))
    config["gatewayList"][gateway_sn]["video_id"] = params["video_id"]
    uuid_tid = str(uuid4())
    uuid_bid = str(uuid4())
    liveJson = {
        "tid": uuid_tid,
        "bid": uuid_bid,
        "method": "live_start_push",
        "data": {
            "url_type": params["url_type"],
            "url": params["url"],
            "video_id": params["video_id"],
            "video_quality": params["video_quality"]
        }
    }
    mqtt_client.publish('thing/product/'+gateway_sn+'/services', json.dumps(liveJson), qos=1)

def MQTT_LIVE_UPDATE(params):
    gateway_sn = ""
    arrVideo = params["video_id"].split("/")
    for key, value in config["gatewayList"].items():
        if value["aircraft"] == arrVideo[0]:
            gateway_sn = key
            break
    uuid_tid = str(uuid4())
    uuid_bid = str(uuid4())
    updateJson = {
        "tid": uuid_tid,
        "bid": uuid_bid,
        "method": "live_set_quality",
        "data": {
            "video_id": config["gatewayList"][gateway_sn]["video_id"],
            "video_quality": 0
        },
        "timestamp": str(int(datetime.datetime.now().timestamp() * 1000))
    }
    mqtt_client.publish('thing/product/'+gateway_sn+'/services', json.dumps(updateJson), qos=1)



'''
for export function to use mqtt at other script
'''
# publish
def mqttPublish(topic, message, options=None, qos=None):
    return mqtt_client.publish(topic, message, qos=0)

# subscribe
def mqttSubscribe(topic, options=None, qos=None):
    return mqtt_client.subscribe(topic, qos=0)

# listen
def mqttListen(topic, message, packet):
    return mqtt_client.on_message(topic, message, packet)



try:
    mqtt_client.loop_start()
except:
    print("[error!]")
    pass