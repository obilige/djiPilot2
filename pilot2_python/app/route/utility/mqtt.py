import paho.mqtt.client as mqtt

import random
import json
from uuid import uuid4
import datetime
from collections import defaultdict

# params 설정해주기
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
    topic = msg.topic
    message = msg.payload.decode("utf-8")
    json_data = json.loads(message)
    
    split_topic = topic.split('/')
    if split_topic[0] == "sys" & split_topic[1] == "product" & split_topic[3] == "status":
        if topic in params["topicList"] & params["topicList"].get(topic) != json.dumps(json_data):
            params["topicList"][topic] = json.dumps(json_data)
            print("[MQTT-", topic, "]", "\t", json.dumps(json_data))
        else:
            params["topicList"][topic] = json.dumps(json_data)
            print("[MQTT-", topic, "]", "\t", json.dumps(json_data))
    
        gateway_sn = split_topic[2]
        # filter(조건, 반복해서 읽을 데이터) : 조건에 맞는 데이터만 뽑아내는 파이썬 내장함수
        pObj = next(filter(
            lambda x:
                x["domain"] == json_data["data"]["domain"]
            and x["type"] == json_data["data"]["type"]
            and x["sub_type"] == json_data["data"]["sub_type"], params["productList"]
        ))
        online_json = {
            "biz_code": "device_online",
            "version": json_data["data"]["version"],
            "timestamp": str(int(datetime.datetime.now().timestamp() * 1000)),
            "data": {
                "sn": gateway_sn,
                "device_model": {
                    "domain": json_data["data"]["domain"],
                    "key": f"{json_data['data']['domain']}-{json_data['data']['type']}-{json_data['data']['sub_type']}",
                    "sub_type": json_data["data"]["sub_type"],
                    "type": json_data["data"]["type"]
                },
                "online_status": True,
                "device_callsign": pObj["name"],
                "model": pObj["name"],
                "bound_status": True,
                "gateway_sn": "",
                "domain": json_data["data"]["domain"]
            }
        }
        
        # 게이트웨이에 감지된 드론, 컨트롤러 status update // 게이트웨이에 없으면 첫번째 로그인인 것!
        if gateway_sn not in params["gatewayList"]:
            device_status = next(filter(lambda x: x["sn"] == gateway_sn, params["gatewayList"]))
            device_status['bound_status'] = True
            device_status['online_status'] = True
        
            params["gatewayList"][gateway_sn]["tid"] = json_data["tid"]
            params["gatewayList"][gateway_sn]["bid"] = json_data["bid"]
            params["gatewayList"][gateway_sn]["device_online1"] = online_json
            params["gatewayList"][gateway_sn]["bizCode"] = {"device_online1"}
        # 게이트웨이에 있으면 일단 tid, bid만 게이트웨이에 등록
        else:
            params["gatewayList"][gateway_sn]["tid"] = json_data["tid"]
            params["gatewayList"][gateway_sn]["bid"] = json_data["bid"]
        
        # 두 대 이상 접속하는 경우, sub_devices가 0에서 1로 바뀜    
        if len(json_data["data"]["sub_devices"]) > 0:
            if "device_online2" in params["gatewayList"][gateway_sn]:
                params['gatewayList'][gateway_sn]['bizCode'] = "device_online2"
            else:
                sub_json = json_data['sub_devices'][0]
                online_sub = {
                    "biz_code": "device_online",
                    "version": json_data["data"]["version"],
                    "timestamp": str(int(datetime.datetime.now().timestamp() * 1000)),
                    "data": {
                        "sn": sub_json["sn"],
                        "device_model": {"domain": sub_json["domain"], "key": f"{sub_json['domain']}-{sub_json['type']}-{sub_json['sub_type']}", "sub_type": sub_json["sub_type"], "type": sub_json["type"]},
                        "online_status": True,
                        "device_callsign": pObj["name"],
                        "model": pObj["name"],
                        "bound_status": True,
                        "gateway_sn": gateway_sn,
                        "domain": sub_json["domain"]
                    }
                }
                sub_device_status = next(filter(lambda x: x["sn"] == gateway_sn, params["gatewayList"]))
                sub_device_status["bound_status"] = True
                sub_device_status["online_status"] = True
                params["gatewayList"][gateway_sn]["aircraft"] = sub_json["sn"]
                params["gatewayList"][gateway_sn]["device_online2"] = online_sub
                params["gatewayList"][gateway_sn]["bizCode"].add("device_online2")
            
            
            



# 클라이언트 생성 및 접속(websocket)
mqtt_client = mqtt.Client(client_id=client_id, transport=transport)
mqtt_client.ws_set_options(path="/mqtt", headers=None)

# 클라이언트에 앞서 선언한 함수 붙이기
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.on_error = on_error
mqtt_client.on_reconnect = on_reconnect
mqtt_client.on_close = on_close
mqtt_client.on_disconnect = on_disconnect
mqtt_client.on_packetsend = on_packetsend
mqtt_client.on_packetreceive = on_packetreceive

# mqtt 메세지 전송, 수신 loop로 계속 이어지도록 하기
mqtt_client.loop_start()