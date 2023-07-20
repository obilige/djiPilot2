import paho.mqtt.client as mqtt

import random
import json
from uuid import uuid4
import datetime
from collections import defaultdict

# params 설정해주기
host = 'emqx-broker'
port = 8083
# client_id는 main.py -> websocket 요청시 들어오는 client_id를 입력해주는 것으로 대체
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
device_online = {i:f"device_offline{i}" for i in range(len(params['device'])/2)} #리모컨이랑 드론이 한쌍



class emqx:
    def __init__(self):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.transport = transport
        self.topic = topic
        self.params = params # params는 개발 편의 위해 하드셋팅. 추후 DB쿼리 결과 등으로 소프트하게 변경
        self.device_online = device_online

    def on_connect(self, client, userdata, flags, rc):
        '''mqtt 연결시 아래 topic들을 구독해야함(브로커로부터 데이터, 메세지 받기 위해)'''
        print("[MQTT] connect")
        
        client.subscribe('sys/product/+/status')
        client.subscribe('sys/product/+/status_reply')
        client.subscribe('thing/product/#')

    def on_error(self, client, userdata, error):
        print("[MQTT-error :", error)

    def on_reconnect(self, client):
        print("[MQTT-reconnect]")

    def on_close(self, client):
        print("[MQTT-close]")

    def on_disconnect(self, client, userdata, rc):
        print("[MQTT-disconnect]")

    def on_packetsend(self, client, packet):
        print("[MQTT-send Packet]")

    def on_packetreceive(self, client, packet):
        print("[MQTT-receive Packet]")

    def on_message(self, client, userdata, msg):
        ''' Main Function '''
        print("[MQTT]-receive Message from broker")
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
                lambda x: # 필터 조건
                    x["domain"] == json_data["data"]["domain"]
                    and x["type"] == json_data["data"]["type"]
                    and x["sub_type"] == json_data["data"]["sub_type"],
                params["productList"] # 필터 걸 데이터(반복 돌 수 있는 복수 데이터 집합)
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
            
            # 게이트웨이에 감지된 드론, 컨트롤러 status update // 게이트웨이에 없으면 첫번째 로그인!
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
            
            # 두 대 이상 접속하는 경우, sub_devices로 데이터가 들어옴    
            if len(json_data["data"]["sub_devices"]) > 0:
                sub_online_number = len(json_data["data"]["sub_devices"])
                if "device_online2" in params["gatewayList"][gateway_sn]:
                    # device_online1이 이미 gateway에 있는 경우, 2를 추가
                    params['gatewayList'][gateway_sn]['bizCode'].add(f"device_online{sub_online_number+1}")
                else:
                    sub_json = json_data['sub_devices'][sub_online_number-1]
                    online_sub = {
                        "biz_code": "device_online",
                        "version": json_data["data"]["version"],
                        "timestamp": str(int(datetime.datetime.now().timestamp() * 1000)),
                        "data": {
                            "sn": sub_json["sn"],
                            "device_model": {
                                "domain": sub_json["domain"],
                                "key": f"{sub_json['domain']}-{sub_json['type']}-{sub_json['sub_type']}",
                                "sub_type": sub_json["sub_type"],
                                "type": sub_json["type"]
                            },
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
                    params["gatewayList"][gateway_sn][f"device_online{sub_online_number+1}"] = online_sub
                    params["gatewayList"][gateway_sn]["bizCode"].add(f"device_online{sub_online_number+1}")
            
            # 접속한 두 드론 중 하나가 로그아웃하면?
            # 현재 방법은 두 대일때만 유효. sub_devices 수와 gateway 수가 다를 때, 하나가 로그아웃한 것이므로 이 때 로그아웃한 기종을 찾아 online 넘버를 지워주는 작업 필요
            elif len(json_data["data"]["sub_devices"]) == 0 and "device_online2" in params["gatewayList"][gateway_sn]:
                online_sub_json = params["gatewayList"][gateway_sn]["device_online2"]
                online_sub_json["biz_code"] = "device_offline"
                online_sub_json["timestamp"] = str(int(datetime.datetime.now().timestamp() * 1000))
                online_sub_json["data"]["online_status"] = False
                online_sub_json["data"]["bound_status"] = False
                online_sub_json["data"]["gateway_sn"] = ""
                print("\t++++ set device_online2", json.dumps(online_sub_json["data"]))
                params["gatewayList"][gateway_sn]["device_offline2"] = online_sub_json
                del params["gatewayList"][gateway_sn]["device_online2"]
                params["gatewayList"][gateway_sn]["bizCode"].add("device_offline2")
                params["gatewayList"][gateway_sn]["bizCode"].add("device_online1")
                del params["gatewayList"][gateway_sn]["aircraft"]
                
                
            elif len(json_data["data"]["sub_devices"]) < len(params['gatewayList'][gateway_sn]['bizCode']):
                pass
            
    def client(self, client_id):
        mqtt_client = mqtt.Client(client_id=client_id, transport=transport)
        mqtt_client.ws_set_options(path="/mqtt", headers=None)

        # 클라이언트에 앞서 선언한 함수 붙이기
        mqtt_client.on_connect = self.on_connect
        mqtt_client.on_message = self.on_message
        mqtt_client.on_error = self.on_error
        mqtt_client.on_reconnect = self.on_reconnect
        mqtt_client.on_close = self.on_close
        mqtt_client.on_disconnect = self.on_disconnect
        mqtt_client.on_packetsend = self.on_packetsend
        mqtt_client.on_packetreceive = self.on_packetreceive

        # mqtt 메세지 전송, 수신 loop로 계속 이어지도록 하기
        mqtt_client.loop_start()
        
        return mqtt_client
        
        
















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
            and x["sub_type"] == json_data["data"]["sub_type"],
            params["productList"]
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
        
        # 게이트웨이에 감지된 드론, 컨트롤러 status update // 게이트웨이에 없으면 첫번째 로그인!
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
        
        # 두 대 이상 접속하는 경우, sub_devices로 데이터가 들어옴    
        if len(json_data["data"]["sub_devices"]) > 0:
            sub_online_number = len(json_data["data"]["sub_devices"])
            if "device_online2" in params["gatewayList"][gateway_sn]:
                # device_online1이 이미 gateway에 있는 경우, 2를 추가
                params['gatewayList'][gateway_sn]['bizCode'].add(f"device_online{sub_online_number+1}")
            else:
                sub_json = json_data['sub_devices'][sub_online_number-1]
                online_sub = {
                    "biz_code": "device_online",
                    "version": json_data["data"]["version"],
                    "timestamp": str(int(datetime.datetime.now().timestamp() * 1000)),
                    "data": {
                        "sn": sub_json["sn"],
                        "device_model": {
                            "domain": sub_json["domain"],
                            "key": f"{sub_json['domain']}-{sub_json['type']}-{sub_json['sub_type']}",
                            "sub_type": sub_json["sub_type"],
                            "type": sub_json["type"]
                        },
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
                params["gatewayList"][gateway_sn][f"device_online{sub_online_number+1}"] = online_sub
                params["gatewayList"][gateway_sn]["bizCode"].add(f"device_online{sub_online_number+1}")
        
        # 접속한 두 드론 중 하나가 로그아웃하면?
        # 현재 방법은 두 대일때만 유효. sub_devices 수와 gateway 수가 다를 때, 하나가 로그아웃한 것이므로 이 때 로그아웃한 기종을 찾아 online 넘버를 지워주는 작업 필요
        elif len(json_data["data"]["sub_devices"]) == 0 and "device_online2" in params["gatewayList"][gateway_sn]:
            online_sub_json = params["gatewayList"][gateway_sn]["device_online2"]
            online_sub_json["biz_code"] = "device_offline"
            online_sub_json["timestamp"] = str(int(datetime.datetime.now().timestamp() * 1000))
            online_sub_json["data"]["online_status"] = False
            online_sub_json["data"]["bound_status"] = False
            online_sub_json["data"]["gateway_sn"] = ""
            print("\t++++ set device_online2", json.dumps(online_sub_json["data"]))
            params["gatewayList"][gateway_sn]["device_offline2"] = online_sub_json
            del params["gatewayList"][gateway_sn]["device_online2"]
            params["gatewayList"][gateway_sn]["bizCode"].add("device_offline2")
            params["gatewayList"][gateway_sn]["bizCode"].add("device_online1")
            del params["gatewayList"][gateway_sn]["aircraft"]
            
            
        elif len(json_data["data"]["sub_devices"]) < len(params['gatewayList'][gateway_sn]['bizCode']):
            pass



# 클라이언트 생성 및 접속(websocket)
mqtt_client = mqtt.Client(client_id=client_id, transport=transport)
mqtt_client.ws_set_options(path="/mqtt", headers=None)

mqtt_client.subscribe()

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