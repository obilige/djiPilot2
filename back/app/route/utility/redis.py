import redis

class redis:
    def __init__(self, **config):
        self.host = "redis"
        self.port = 6379
        self.decode_response = True

    def connect(self, **db):
        return redis.Redis(host=self.host, port=self.port, decode_responses=self.decode_response, db=db if db else 0)

    def json(self, **device_list):
        r_json = self.connect().json()
        # 추후 db에서 긁어오도록 만들 것. 제품등록 기능 구현 후 진행
        connection_list = {
            "gatewayList": {},
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
        }
        r_json.set("pilot2_connection", connection_list)
        return r_json

    def set(self, key, value):
        self.json.set(key, value)
    
    def get(self, key, value):
        return self.json.get(key, value)