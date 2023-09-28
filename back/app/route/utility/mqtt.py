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

    # mqtt 주요 액션별 코드 진행 함수
    def on_connect(self, client, userdata, flags, rc):
        '''mqtt 연결시 아래 topic들을 구독해야함(브로커로부터 데이터, 메세지 받기 위해)'''
        print("[MQTT] connect")

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
                    params['gatewayList'][gateway_sn]['bizCode'].add(f"device_online{sub_online_number}")
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
                
            # elif len(json_data["data"]["sub_devices"]) < len(params['gatewayList'][gateway_sn]['bizCode']):

            self.MQTT_STATUS_REPLY(client, split_topic[2])

        elif split_topic[0] == "sys" and split_topic[1] == "product" and split_topic[3] == "status_reply":
            if topic in params["topicList"]:
                if params["topicList"][topic] != json.dumps(json_data):
                    params["topicList"][topic] = json.dumps(json_data)
                    print("[MQTT-", topic, "]", "\t", json.dumps(json_data))
            else:
                params["topicList"][topic] = json.dumps(json_data)
                print("[MQTT-", topic, "]", "\t", json.dumps(json_data))

        elif split_topic[0] == "thing" and split_topic[1] == "product" and split_topic[3] == "osd":
            sn = split_topic[2]
            gateway_sn = json_data["gateway"]
            del json_data["bid"]
            del json_data["tid"]
            if topic in params["topicList"]:
                if params["topicList"][topic] != json.dumps(json_data):
                    params["topicList"][topic] = json.dumps(json_data)
                    print("[MQTT-", topic, "]", "\t", json.dumps(json_data))
            else:
                params["topicList"].set(topic, json.dumps(json_data))
                print("[MQTT-", topic, "]", "\t", json.dumps(json_data))

            if gateway_sn in params["gatewayList"]:
                if json_data["data"]["live_status"]:
                    params["gatewayList"][gateway_sn]["gateway_osd"] = {"biz_code": "gateway_osd", "version": "1.0", "timestamp": str(int(datetime.datetime.now().timestamp() * 1000)), "data": {"host": json_data["data"], "sn": sn}}
                    params["gatewayList"][gateway_sn]["bizCode"].add("gateway_osd")
                else:
                    params["gatewayList"][gateway_sn]["device_osd"] = {"biz_code": "device_osd", "version": "1.0", "timestamp": str(int(datetime.datetime.now().timestamp() * 1000)), "data": {"host": json_data["data"], "sn": sn}}
                    params["gatewayList"][gateway_sn]["bizCode"].add("device_osd")
                params["gatewayList"][gateway_sn]["osd"] = {"biz_code": "device_osd", "version": "1.0", "timestamp": str(int(datetime.datetime.now().timestamp() * 1000)), "data": {"sn": sn}}
                params["gatewayList"][gateway_sn]["bizCode"].add("osd")

        elif split_topic[0] == "thing" and split_topic[1] == "product" and split_topic[3] == "events":
            del json_data["bid"]
            del json_data["tid"]
            if (topic + "|" + json_data["data"]["event"]) in params["topicList"]:
                if params["topicList"][topic + "|" + json_data["data"]["event"]] != json.dumps(json_data):
                    params["topicList"][topic + "|" + json_data["data"]["event"]] = json.dumps(json_data)
                    print("[MQTT-", topic, "]", "\t", json.dumps(json_data))
            else:
                params["topicList"][topic + "|" + json_data["data"]["event"]] = json.dumps(json_data)
                print("[MQTT-", topic, "]", "\t", json.dumps(json_data))

        elif split_topic[0] == "thing" and split_topic[1] == "product" and split_topic[3] == "state":
            del json_data["bid"]
            del json_data["tid"]
            gateway_sn = split_topic[2]
            if topic in params["topicList"]:
                if params["topicList"][topic] != json.dumps(json_data):
                    params["topicList"][topic] = json.dumps(json_data)
                    print("[MQTT-", topic, "]", "\t", json.dumps(json_data))
            else:
                params["topicList"].set(topic, json.dumps(json_data))
                print("[MQTT-", topic, "]", "\t", json.dumps(json_data))

            if "live_capacity" in json_data["data"]:
                if "device_list" in json_data["data"]["live_capacity"]:
                    if len(json_data["data"]["live_capacity"]["device_list"]) > 0:
                        params["deviceList"].find(lambda ele: ele["sn"] == gateway_sn)["camera_index"] = json_data["data"]["live_capacity"]["device_list"][0]["camera_list"][0]["camera_index"]
                        params["deviceList"].find(lambda ele: ele["sn"] == gateway_sn)["video_list"] = json_data["data"]["live_capacity"]["device_list"][0]["camera_list"][0]["video_list"]

        else:
            print("======================================[MQTT topic] : ", topic, json.dumps(json_data))        


    def client(self, client_id):
        self.mqtt_client = mqtt.Client(client_id=client_id, transport=transport)
        self.mqtt_client.ws_set_options(path="/mqtt", headers=None)

        # 클라이언트에 앞서 선언한 함수 붙이기
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.on_error = self.on_error
        self.mqtt_client.on_reconnect = self.on_reconnect
        self.mqtt_client.on_close = self.on_close
        self.mqtt_client.on_disconnect = self.on_disconnect
        self.mqtt_client.on_packetsend = self.on_packetsend
        self.mqtt_client.on_packetreceive = self.on_packetreceive

        # mqtt 메세지 전송, 수신 loop로 계속 이어지도록 하기
        self.mqtt_client.loop_start()
    
    # mqtt function
    def MQTT_STATUS_REPLY(self, gateway_sn):
        self.mqtt_client.publish('sys/product/' + gateway_sn + '/status_reply', json.dumps({
            "tid": params["gatewayList"][gateway_sn]["tid"],
            "bid": params["gatewayList"][gateway_sn]["bid"],
            "method": "update_topo",
            "data": {"result": 0},
            "timestamp": str(int(datetime.datetime.now().timestamp() * 1000))
        }), qos=0)

    def MQTT_LIVE_STOP(self, params):
        gateway_sn = ""
        arrVideo = params["video_id"].split("/")
        for key, value in params["gatewayList"].items():
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
                "video_id": params["gatewayList"][gateway_sn]["video_id"],
            },
            "timestamp": str(int(datetime.datetime.now().timestamp() * 1000))
        }
        self.mqtt_client.publish('thing/product/'+gateway_sn+'/services', json.dumps(stopJson), qos=1)

    def MQTT_LIVE_START(self, params):
        gateway_sn = ""
        arrVideo = params["video_id"].split("/")
        for key, value in params["gatewayList"].items():
            if value["aircraft"] == arrVideo[0]:
                gateway_sn = key
                break
        print("[MQTT_LIVE_START] sn", gateway_sn, "params", json.dumps(params))
        params["gatewayList"][gateway_sn]["video_id"] = params["video_id"]
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
        self.mqtt_client.publish('thing/product/'+gateway_sn+'/services', json.dumps(liveJson), qos=1)

    def MQTT_LIVE_UPDATE(self, params):
        gateway_sn = ""
        arrVideo = params["video_id"].split("/")
        for key, value in params["gatewayList"].items():
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
                "video_id": params["gatewayList"][gateway_sn]["video_id"],
                "video_quality": 0
            },
            "timestamp": str(int(datetime.datetime.now().timestamp() * 1000))
        }
        self.mqtt_client.publish('thing/product/'+gateway_sn+'/services', json.dumps(updateJson), qos=1)

    '''
    for export function to use mqtt at other script
    '''
    # publish
    def mqttPublish(self, topic, message, options=None, qos=None):
        return self.mqtt_client.publish(topic, message, qos=0)

    # subscribe
    def mqttSubscribe(self, topic, options=None, qos=None):
        # self.mqtt_client.subscribe('sys/product/+/status')
        # self.mqtt_client.subscribe('sys/product/+/status_reply')
        # self.mqtt_client.subscribe('thing/product/#')
        return self.mqtt_client.subscribe(self.topic, qos=1)
    
    def mqttUnsubscribe(self, topic, options=None, qos=None):
        # self.mqtt_client.unsubscribe('sys/product/+/status')
        # self.mqtt_client.unsubscribe('sys/product/+/status_reply')
        # self.mqtt_client.unsubscribe('thing/product/#')
        return self.mqtt_client.unsubscribe(self.topic, qos=0)

    # listen
    def mqttListen(self, topic, message, packet):
        return self.mqtt_client.on_message(topic, message, packet)
        














