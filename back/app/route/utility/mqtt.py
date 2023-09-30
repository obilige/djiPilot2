import paho.mqtt.client as mqtt

import random
import json
from uuid import uuid4
import datetime
from collections import defaultdict
import redis



class emqx:
    def __init__(self, **config):
        self.host = config['host'] if config else "emqx-broker"
        self.port = config['host'] if config else 8083
        self.username = config['host'] if config else 'emqx'
        self.password = config['host'] if config else 'public'
        self.transport = config['host'] if config else 'websockets'
        self.client_id = f'subscribe-{random.randint(0, 100)}'
        # topic은 wireshark로 sample packet 잡아서 mqtt로 보내는 topic 확인한 것. 드론에서 보내는 고정값이므로 하드코딩
        self.topic = [('sys/product/+/status', 0), 
                      ('sys/product/+/status_reply', 0),
                      ('thing/product/#',0) ,]
        self.redis = redis.Redis().json()

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
            if topic in self.redis["topicList"] & self.redis["topicList"].get(topic) != json.dumps(json_data):
                self.redis["topicList"][topic] = json.dumps(json_data)
                print("[MQTT-", topic, "]", "\t", json.dumps(json_data))
            else:
                self.redis["topicList"][topic] = json.dumps(json_data)
                print("[MQTT-", topic, "]", "\t", json.dumps(json_data))
        
            gateway_sn = split_topic[2]
            # filter(조건, 반복해서 읽을 데이터) : 조건에 맞는 데이터만 뽑아내는 파이썬 내장함수
            pObj = next(filter(
                lambda x: # 필터 조건
                    x["domain"] == json_data["data"]["domain"]
                    and x["type"] == json_data["data"]["type"]
                    and x["sub_type"] == json_data["data"]["sub_type"],
                self.redis["productList"] # 필터 걸 데이터(반복 돌 수 있는 복수 데이터 집합)
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
            if gateway_sn not in self.redis["gatewayList"]:
                device_status = next(filter(lambda x: x["sn"] == gateway_sn, self.redis["gatewayList"]))
                device_status['bound_status'] = True
                device_status['online_status'] = True
            
                self.redis["gatewayList"][gateway_sn]["tid"] = json_data["tid"]
                self.redis["gatewayList"][gateway_sn]["bid"] = json_data["bid"]
                self.redis["gatewayList"][gateway_sn]["device_online1"] = online_json
                self.redis["gatewayList"][gateway_sn]["bizCode"] = {"device_online1"}
            # 게이트웨이에 있으면 일단 tid, bid만 게이트웨이에 등록
            else:
                self.redis["gatewayList"][gateway_sn]["tid"] = json_data["tid"]
                self.redis["gatewayList"][gateway_sn]["bid"] = json_data["bid"]
            
            # 두 대 이상 접속하는 경우, sub_devices로 데이터가 들어옴    
            if len(json_data["data"]["sub_devices"]) > 0:
                sub_online_number = len(json_data["data"]["sub_devices"])
                if "device_online2" in self.redis["gatewayList"][gateway_sn]:
                    # device_online1이 이미 gateway에 있는 경우, 2를 추가
                    self.redis['gatewayList'][gateway_sn]['bizCode'].add(f"device_online{sub_online_number}")
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
                    sub_device_status = next(filter(lambda x: x["sn"] == gateway_sn, self.redis["gatewayList"]))
                    sub_device_status["bound_status"] = True
                    sub_device_status["online_status"] = True
                    self.redis["gatewayList"][gateway_sn]["aircraft"] = sub_json["sn"]
                    self.redis["gatewayList"][gateway_sn][f"device_online{sub_online_number+1}"] = online_sub
                    self.redis["gatewayList"][gateway_sn]["bizCode"].add(f"device_online{sub_online_number+1}")
            
            # 접속한 두 드론 중 하나가 로그아웃하면?
            # 현재 방법은 두 대일때만 유효. sub_devices 수와 gateway 수가 다를 때, 하나가 로그아웃한 것이므로 이 때 로그아웃한 기종을 찾아 online 넘버를 지워주는 작업 필요
            elif len(json_data["data"]["sub_devices"]) == 0 and "device_online2" in self.redis["gatewayList"][gateway_sn]:
                online_sub_json = self.redis["gatewayList"][gateway_sn]["device_online2"]
                online_sub_json["biz_code"] = "device_offline"
                online_sub_json["timestamp"] = str(int(datetime.datetime.now().timestamp() * 1000))
                online_sub_json["data"]["online_status"] = False
                online_sub_json["data"]["bound_status"] = False
                online_sub_json["data"]["gateway_sn"] = ""
                print("\t++++ set device_online2", json.dumps(online_sub_json["data"]))
                self.redis["gatewayList"][gateway_sn]["device_offline2"] = online_sub_json
                del self.redis["gatewayList"][gateway_sn]["device_online2"]
                self.redis["gatewayList"][gateway_sn]["bizCode"].add("device_offline2")
                self.redis["gatewayList"][gateway_sn]["bizCode"].add("device_online1")
                del self.redis["gatewayList"][gateway_sn]["aircraft"]
                
            # elif len(json_data["data"]["sub_devices"]) < len(self.redis['gatewayList'][gateway_sn]['bizCode']):

            self.MQTT_STATUS_REPLY(client, split_topic[2])

        elif split_topic[0] == "sys" and split_topic[1] == "product" and split_topic[3] == "status_reply":
            if topic in self.redis["topicList"]:
                if self.redis["topicList"][topic] != json.dumps(json_data):
                    self.redis["topicList"][topic] = json.dumps(json_data)
                    print("[MQTT-", topic, "]", "\t", json.dumps(json_data))
            else:
                self.redis["topicList"][topic] = json.dumps(json_data)
                print("[MQTT-", topic, "]", "\t", json.dumps(json_data))

        elif split_topic[0] == "thing" and split_topic[1] == "product" and split_topic[3] == "osd":
            sn = split_topic[2]
            gateway_sn = json_data["gateway"]
            del json_data["bid"]
            del json_data["tid"]
            if topic in self.redis["topicList"]:
                if self.redis["topicList"][topic] != json.dumps(json_data):
                    self.redis["topicList"][topic] = json.dumps(json_data)
                    print("[MQTT-", topic, "]", "\t", json.dumps(json_data))
            else:
                self.redis["topicList"].set(topic, json.dumps(json_data))
                print("[MQTT-", topic, "]", "\t", json.dumps(json_data))

            if gateway_sn in self.redis["gatewayList"]:
                if json_data["data"]["live_status"]:
                    self.redis["gatewayList"][gateway_sn]["gateway_osd"] = {"biz_code": "gateway_osd", "version": "1.0", "timestamp": str(int(datetime.datetime.now().timestamp() * 1000)), "data": {"host": json_data["data"], "sn": sn}}
                    self.redis["gatewayList"][gateway_sn]["bizCode"].add("gateway_osd")
                else:
                    self.redis["gatewayList"][gateway_sn]["device_osd"] = {"biz_code": "device_osd", "version": "1.0", "timestamp": str(int(datetime.datetime.now().timestamp() * 1000)), "data": {"host": json_data["data"], "sn": sn}}
                    self.redis["gatewayList"][gateway_sn]["bizCode"].add("device_osd")
                self.redis["gatewayList"][gateway_sn]["osd"] = {"biz_code": "device_osd", "version": "1.0", "timestamp": str(int(datetime.datetime.now().timestamp() * 1000)), "data": {"sn": sn}}
                self.redis["gatewayList"][gateway_sn]["bizCode"].add("osd")

        elif split_topic[0] == "thing" and split_topic[1] == "product" and split_topic[3] == "events":
            del json_data["bid"]
            del json_data["tid"]
            if (topic + "|" + json_data["data"]["event"]) in self.redis["topicList"]:
                if self.redis["topicList"][topic + "|" + json_data["data"]["event"]] != json.dumps(json_data):
                    self.redis["topicList"][topic + "|" + json_data["data"]["event"]] = json.dumps(json_data)
                    print("[MQTT-", topic, "]", "\t", json.dumps(json_data))
            else:
                self.redis["topicList"][topic + "|" + json_data["data"]["event"]] = json.dumps(json_data)
                print("[MQTT-", topic, "]", "\t", json.dumps(json_data))

        elif split_topic[0] == "thing" and split_topic[1] == "product" and split_topic[3] == "state":
            del json_data["bid"]
            del json_data["tid"]
            gateway_sn = split_topic[2]
            if topic in self.redis["topicList"]:
                if self.redis["topicList"][topic] != json.dumps(json_data):
                    self.redis["topicList"][topic] = json.dumps(json_data)
                    print("[MQTT-", topic, "]", "\t", json.dumps(json_data))
            else:
                self.redis["topicList"].set(topic, json.dumps(json_data))
                print("[MQTT-", topic, "]", "\t", json.dumps(json_data))

            if "live_capacity" in json_data["data"]:
                if "device_list" in json_data["data"]["live_capacity"]:
                    if len(json_data["data"]["live_capacity"]["device_list"]) > 0:
                        self.redis["deviceList"].find(lambda ele: ele["sn"] == gateway_sn)["camera_index"] = json_data["data"]["live_capacity"]["device_list"][0]["camera_list"][0]["camera_index"]
                        self.redis["deviceList"].find(lambda ele: ele["sn"] == gateway_sn)["video_list"] = json_data["data"]["live_capacity"]["device_list"][0]["camera_list"][0]["video_list"]

        else:
            print("======================================[MQTT topic] : ", topic, json.dumps(json_data))        


    def client(self):
        self.mqtt_client = mqtt.Client(client_id=self.client_id, transport=self.transport)
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
            "tid": self.redis["gatewayList"][gateway_sn]["tid"],
            "bid": self.redis["gatewayList"][gateway_sn]["bid"],
            "method": "update_topo",
            "data": {"result": 0},
            "timestamp": str(int(datetime.datetime.now().timestamp() * 1000))
        }), qos=0)

    def MQTT_LIVE_STOP(self):
        gateway_sn = ""
        arrVideo = self.redis["video_id"].split("/")
        for key, value in self.redis["gatewayList"].items():
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
                "video_id": self.redis["gatewayList"][gateway_sn]["video_id"],
            },
            "timestamp": str(int(datetime.datetime.now().timestamp() * 1000))
        }
        self.mqtt_client.publish('thing/product/'+gateway_sn+'/services', json.dumps(stopJson), qos=1)

    def MQTT_LIVE_START(self):
        gateway_sn = ""
        arrVideo = self.redis["video_id"].split("/")
        for key, value in self.redis["gatewayList"].items():
            if value["aircraft"] == arrVideo[0]:
                gateway_sn = key
                break
        print("[MQTT_LIVE_START] sn", gateway_sn, "self.redis", json.dumps(self.redis))
        self.redis["gatewayList"][gateway_sn]["video_id"] = self.redis["video_id"]
        uuid_tid = str(uuid4())
        uuid_bid = str(uuid4())
        liveJson = {
            "tid": uuid_tid,
            "bid": uuid_bid,
            "method": "live_start_push",
            "data": {
                "url_type": self.redis["url_type"],
                "url": self.redis["url"],
                "video_id": self.redis["video_id"],
                "video_quality": self.redis["video_quality"]
            }
        }
        self.mqtt_client.publish('thing/product/'+gateway_sn+'/services', json.dumps(liveJson), qos=1)

    def MQTT_LIVE_UPDATE(self):
        gateway_sn = ""
        arrVideo = self.redis["video_id"].split("/")
        for key, value in self.redis["gatewayList"].items():
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
                "video_id": self.redis["gatewayList"][gateway_sn]["video_id"],
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
        














