const API_SERVER = 'http://localhost:8095/';
const WS_SERVER = 'ws://localhost:8095/';
const uuidv4 = uuid.v4;
const myUUID = uuidv4();
let isMqttConnected = false;
var latitude = 36.8911;
var longitude = 127.82;
let client = '';
let socket = '';
let isStop = true;  // 멈춤여부: true = 멈춤
let device_sn = ''; //'1581F5FKD232800D2TK8';
let device_sn2 = ''; //'5YSZL260021E9E';
let device_snTwo = ''; //'1581F5FKD232800D2TK8';
let device_sn2Two = ''; //'5YSZL260021E9E';
let elevation = 0;
const login = async function (body) {
    try {
        let id = body.username;
        let password = body.password;
        let data = await loginPilot(id, password, body);
        console.log('login성공');
        return data;
    } catch (error) {
        console.error('Error in login:', error);
        return error;
    }
}
const loginPilot = async (id, password, body) => {
    try {
        const response = await axios.get(API_SERVER + `api/auth/users/getRsaKey`);
        const publicKey = response.data;
        console.log('Received public key:', publicKey);

        const encrypt = new JSEncrypt();
        encrypt.setPublicKey(publicKey);

        var encrypt_id = encrypt.encrypt(id);
        var encrypt_pw = encrypt.encrypt(password);

        const authResponse = await axios.post(
            API_SERVER + `api/auth/users/login`,
            { encrypt_id, encrypt_pw },
            { headers: { 'Content-Type': 'application/json' } }
        );

        return axios.post(
            API_SERVER + `back/manage/api/v1/login`,
            body,
            { headers: { 'Content-Type': 'application/json' } }
        );
    } catch (error) {
        console.error('Error in loginPilot:', error);
        throw error;
    }
};
const requestBody = {
    username: 'admin',
    password: 'visumy00!',
};
const getAircraftSN = () => {
    return returnString(window.djiBridge.platformGetAircraftSN());
};
const getDeviceBySn = async function (workspace_id, device_sn) {
    const url = API_SERVER + `back/manage/api/v1/devices/${workspace_id}/devices/${device_sn}`
    return axios.get(url);
};
const getPlatformInfo = async function () {
    const url = API_SERVER + `back/manage/api/v1/workspaces/current`
    return axios.get(url);
};
const getUserInfo = async function () {
    const url = API_SERVER + `back/manage/api/v1/users/current`
    return axios.get(url);
};
const returnString = (response) => {
    const res = JSON.parse(response)
    return errorHint(res) ? res.data : ''
};
const getTopologies = async function (workspace_id) {
    const url = API_SERVER + `back/manage/api/v1/workspaces/${workspace_id}/devices/topologies`
    return axios.get(url);
};
const getMinio = async function (workspace_id) {
    const url = API_SERVER + `back/storage/api/v1/workspaces/${workspace_id}/sts`
    return axios.post(
        url,
        {},
        { headers: { 'Content-Type': 'application/json' } }
    );
};
const getBinding = async function (device_sn, user_id, workspace_id) {
    const url = API_SERVER + `back/manage/api/v1/devices/${device_sn}/binding`
    return axios.post(
        url,
        { device_sn, user_id, workspace_id },
        { headers: { 'Content-Type': 'application/json' } }
    );
};
const getWayline = async function (workspace_id) {
    const url = API_SERVER + `back/wayline/api/v1/workspaces/${workspace_id}/waylines`;
    // return axios.get(url);
    const params = {
        file_type: 5,
        key: '',
        favorited: false,
        action_type: 0,
        order_by: 'update_time desc',
        page_size: 9,
        page: 1
    };
    axios.get(url, { params })
        .then(response => {
            // 성공적으로 응답을 받았을 때 처리
            // console.log('응답 데이터:', response.data);
        })
        .catch(error => {
            // 오류 발생 시 처리
            console.error('오류:', error);
        });
};

// mqtt 연결 버튼 작동
const onMqttClick = async (access_token) => {
    client = mqtt.connect("ws://localhost:8095/mqtt/", {  // mqtt 접속 주소
        username: 'admin',
        protocol: 'ws',
        password: '$1$S9FNPFRw$3eIO6PO3BlmYyYCoBZn4s1' // local :"user" 테이블에 저장된 admin의 password
    });

    // 추가코드 
    client.on('connect', function () {
        console.log("[MQTT]-connect");
        // 두번 띄우기
        device_sn = document.getElementById("deviceSnInput").value;
        device_sn2 = document.getElementById("deviceSnInput2").value;

        device_snTwo = document.getElementById("deviceSnInputTwo").value;
        device_sn2Two = document.getElementById("deviceSnInput2Two").value;
        mqttTask(device_sn, device_sn2, device_snTwo, device_sn2Two);
    });

    client.on('error', function (error) {
        if (isMqttConnected) console.log("[MQTT]-error : ", error)
    });

    client.on('message', function (topic, message, packet) {

        console.log('메시지 받음????????????????????') // 안받고있음
        const receivedMessage = JSON.parse(message.toString());
        // console.log("[MQTT]-message received", topic, message.toString());
        console.log("[MQTT]-message received::", topic, JSON.parse(message), packet);

    });

    client.on('close', function () {
        console.log("[MQTT]-close");
        isMqttConnected = false;
    });

    client.on('reconnect', function () {
        // console.log("[MQTT]-reconnect");
    });

    client.on('offline', function () {
        console.log("[MQTT]-offline");
        isMqttConnected = false;
    });

    client.on('disconnect', function (packet) {
        console.log("[MQTT]-disconnect");
    });

}

// 콘솔창 object까지 보여주는 코드
var oldConsoleLog = console.log;
console.log = function () {
    var logTextarea = document.getElementById('logTextarea');
    for (var i = 0; i < arguments.length; i++) {
        var argument = arguments[i];
        if (typeof argument === 'object') {
            logTextarea.value += stringifyObject(argument) + ' ';
        } else {
            logTextarea.value += argument + ' ';
        }
    }
    logTextarea.value += '\n';

    // 기존의 console.log도 호출하기
    oldConsoleLog.apply(console, arguments);
};

// 객체를 문자열로 변환하는 사용자 정의 함수
function stringifyObject(obj) {
    var result = '{ ';
    for (var key in obj) {
        if (obj.hasOwnProperty(key)) {
            result += key + ': ' + obj[key] + ', ';
        }
    }
    result = result.replace(/, $/, '');  // 마지막 쉼표 제거
    result += ' }';
    return result;
}

// 웹소켓 연결
const onWebsocketClick = async () => {
    // device_sn = document.getElementById("deviceSnInput").value;
    // device_sn2 = document.getElementById("deviceSnInput2").value;

    // device_sn = document.getElementById("deviceSnInputTwo").value;
    // device_sn2 = document.getElementById("deviceSnInput2Two").value;

    console.log(device_sn)
    console.log(device_sn2)

    const result = await login(requestBody)
        .then(response => {
            // websocket(response.data.data.access_token);
            const token = response.data.data.access_token;
            const url = WS_SERVER + 'back/api/v1/ws' + '?x-auth-token=' + encodeURIComponent(token)
            socket = new WebSocket(url);

            socket.onerror = (error) => {
                console.error('WebSocket Error:', error);
            };

            socket.onopen = () => {
                console.log('[PilotHome.vue]  웹소켓 연결 성공...');
            }

            socket.onmessage = (data) => {
                // 추가 코드
                // console.log('data:::', data.data) // 여기까지는 들어옴
                var json = JSON.parse(data.data); // 여기서 오류 발생 (원래코드)
                console.log('[WS] received: !!!!!!!!!!!!!!!!!!!!!!!!!!!!!', json.biz_code);
                if (json.biz_code == 'device_online') {
                    console.log("[[[device_online]]] 을 수신하면 뭘 해야하나?", json);
                } else if (json.biz_code == 'device_update_topo') {
                    console.log("[[[device_update_topo]]] 을 수신하면 뭘 해야하나?", json);
                    // osd로 상태 보고하면 되나?
                    setInterval(function () { // 위치
                        // if (isStop) clearInterval(interval);
                        latitude += 0.00001;
                        console.log('위도+:', latitude)
                        device_sn = document.getElementById("deviceSnInput").value;
                        device_sn2 = document.getElementById("deviceSnInput2").value;
                        device_snTwo = document.getElementById("deviceSnInputTwo").value;
                        device_sn2Two = document.getElementById("deviceSnInput2Two").value;
                        console.log('device_sn:', device_snTwo)
                        console.log('device_sn2:', device_sn2Two)
                        moveDrone(device_sn, device_sn2, device_snTwo, device_sn2Two);
                    }, 1000);
                } else {
                    console.log('뭐지?????')
                }
            }
        })
        .catch(error => {
            // 오류 발생 시 처리
            console.log(error);
        });
}

const main = async () => {
    try {
        const result = await login(requestBody);
        console.log('로그인 결과:', result);
        // websocket(result.data.data.access_token);

        device_sn = document.getElementById("deviceSnInput").value;
        device_sn2 = document.getElementById("deviceSnInput2").value;

        let user_id = result.data.data.user_id;
        let workspace_id = result.data.data.workspace_id;

        const [deviceInfo, workspace_data, user_data, topologies_data, minio_data, Binding_data, wayline_data] = await Promise.all([
            getDeviceBySn(workspace_id, device_sn),
            getPlatformInfo(),
            getUserInfo(),
            getTopologies(workspace_id),
            getMinio(workspace_id),
            getBinding(device_sn, user_id, workspace_id),
            getWayline(workspace_id),
        ]);
    } catch (error) {
        console.error('로그인 중 오류:', error);
    }
};
function onResetClick() {
    document.getElementById("logTextarea").value = '';
    // 로그 reset
    console.clear();
};
function onNorthClick() {
    latitude += 0.00001;
    moveDrone();
};
function onSouthClick() {
    latitude -= 0.00001;
    moveDrone();
};
function onEastClick() {
    longitude += 0.00001;
    moveDrone();
};
function onWestClick() {
    longitude -= 0.00001;
    moveDrone();
};
function onStopClick() {
    isStop = true;
};
function onPlayClick() {
    isStop = false;
}
function moveDrone(device_sn, device_sn2, device_snTwo, device_sn2Two) { // 드론 이동
    client.publish(`thing/product/${device_sn}/osd`,
        JSON.stringify({
            "bid": "cb3fdd7d-4b70-255b-2259-4a0483a90e27",
            "data": {
                "68-0-0": {
                    "gimbal_pitch": -90, "gimbal_roll": -0.1, "gimbal_yaw": 59.6, "payload_index": "68-0-0", "zoom_factor": 0.56782334384858046
                },
                "attitude_head": 36.300000000000004, "attitude_pitch": 4.1000000000000005, "attitude_roll": 0.30000000000000004,
                "battery": {
                    "batteries": [{
                        "capacity_percent": 90, "firmware_version": "08.75.02.23", "high_voltage_storage_days": 0, "index": 0, "loop_times": 153,
                        "sn": "4ERKL1H6G30XU5", "sub_type": 0, "temperature": 34.2, "type": 0, "voltage": 16674
                    }], "capacity_percent": 90, "landing_power": 9, "remain_flight_time": 0, "return_home_power": 0
                },
                "distance_limit_status": { "distance_limit": 480, "state": 0 }, "elevation": elevation, "firmware_version": "07.01.2001", "gear": 1, "height": -97.639198303222656,
                "height_limit": 220, "home_distance": 0, "horizontal_speed": 0, "latitude": latitude, "longitude": longitude, "mode_code": 0,
                "position_state": { "gps_number": 0, "is_fixed": 0, "quality": 0, "rtk_number": 0 }, "storage": { "total": 60096000, "used": 27910000 },
                "total_flight_distance": 0, "total_flight_time": 0, "track_id": "", "vertical_speed": 0, "wind_direction": 0, "wind_speed": 0
            },
            "tid": "53cae1b6-3ba0-2781-2522-a497d43d731a", "timestamp": 1702259264674, "gateway": `${device_sn2}`
        }));
    client.publish(`thing/product/${device_snTwo}/osd`,
        JSON.stringify({
            "bid": "cb3fdd7d-4b70-255b-2259-4a0483a90e27",
            "data": {
                "68-0-0": {
                    "gimbal_pitch": -90, "gimbal_roll": -0.1, "gimbal_yaw": 59.6, "payload_index": "68-0-0", "zoom_factor": 0.56782334384858046
                },
                "attitude_head": 36.300000000000004, "attitude_pitch": 4.1000000000000005, "attitude_roll": 0.30000000000000004,
                "battery": {
                    "batteries": [{
                        "capacity_percent": 90, "firmware_version": "08.75.02.23", "high_voltage_storage_days": 0, "index": 0, "loop_times": 153,
                        "sn": "4ERKL1H6G30XU5", "sub_type": 0, "temperature": 34.2, "type": 0, "voltage": 16674
                    }], "capacity_percent": 90, "landing_power": 9, "remain_flight_time": 0, "return_home_power": 0
                },
                "distance_limit_status": { "distance_limit": 480, "state": 0 }, "elevation": elevation, "firmware_version": "07.01.2001", "gear": 1, "height": -97.639198303222656,
                "height_limit": 220, "home_distance": 0, "horizontal_speed": 0, "latitude": latitude, "longitude": longitude, "mode_code": 0,
                "position_state": { "gps_number": 0, "is_fixed": 0, "quality": 0, "rtk_number": 0 }, "storage": { "total": 60096000, "used": 27910000 },
                "total_flight_distance": 0, "total_flight_time": 0, "track_id": "", "vertical_speed": 0, "wind_direction": 0, "wind_speed": 0
            },
            "tid": "53cae1b6-3ba0-2781-2522-a497d43d731a", "timestamp": 1702259264674, "gateway": `${device_sn2Two}`
        }));
}
function onTopClick() {
    elevation += 1;
    moveDrone();
}
function onBottomClick() {
    elevation -= 1;
    moveDrone();
}
function mqttTask(device_sn, device_sn2, device_snTwo, device_sn2Two) { // mqtt연결됐을때 구독/발행
    let requestPayloads1 = { "bid": "00000000-0000-0000-0000-000000000000", "data": { "capacity_percent": 90, "height": 0, "latitude": 36.8911, "longitude": 127.8223, "wireless_link": { "4g_freq_band": 5.8, "4g_gnd_quality": 0, "4g_link_state": 0, "4g_quality": 0, "4g_uav_quality": 0, "dongle_number": 0, "link_workmode": 0, "sdr_freq_band": 1, "sdr_link_state": 1, "sdr_quality": 5 } }, "tid": "00000000-0000-0000-0000-000000000000", "timestamp": 1701742231501, "gateway": `${device_sn2}` }
    let requestPayloads2 = { "bid": "00000000-0000-0000-0000-000000000000", "data": { "event": "status_code", "method": "status_code", "output": { "codes": [{ "id": 521142273 }] } }, "tid": "00000000-0000-0000-0000-000000000000", "timestamp": 1701742231507, "gateway": `${device_sn2}` }
    let requestPayloads3 = { "bid": "00000000-0000-0000-0000-000000000000", "data": { "68-0-0": { "gimbal_pitch": 0, "gimbal_roll": 0, "gimbal_yaw": -125.9, "payload_index": "68-0-0", "zoom_factor": 0.56782334384858046 }, "attitude_head": 0, "attitude_pitch": -1, "attitude_roll": 0.4, "battery": { "batteries": [{ "capacity_percent": 81, "firmware_version": "08.75.02.23", "high_voltage_storage_days": 0, "index": 0, "loop_times": 150, "sn": "4ERKL1H6G30XU5", "sub_type": 0, "temperature": 37.8, "type": 0, "voltage": 16340 }], "capacity_percent": 81, "landing_power": 8, "remain_flight_time": 0, "return_home_power": 0 }, "distance_limit_status": { "distance_limit": 480, "state": 0 }, "elevation": 0, "firmware_version": "07.01.2001", "gear": 1, "height": -0.10012054443359375, "height_limit": 150, "home_distance": 0.66433465480804443, "horizontal_speed": 0, "latitude": 36.891093959338257, "longitude": 127.82229967548831, "mode_code": 0, "position_state": { "gps_number": 15, "is_fixed": 0, "quality": 5, "rtk_number": 0 }, "storage": { "total": 60096000, "used": 26204000 }, "total_flight_distance": 0, "total_flight_time": 0, "track_id": "", "vertical_speed": 0, "wind_direction": 0, "wind_speed": 0 }, "tid": "00000000-0000-0000-0000-000000000000", "timestamp": 1701742231508, "gateway": `${device_sn2}` }
    let requestPayloads4 = { "bid": "00000000-0000-0000-0000-000000000000", "data": { "event": "hms", "method": "hms", "output": { "codes": [] } }, "tid": "00000000-0000-0000-0000-000000000000", "timestamp": 1701742231508, "gateway": `${device_sn2}` }

    let requestPayloads5 = { "bid": "00000000-0000-0000-0000-000000000000", "data": { "capacity_percent": 90, "height": 0, "latitude": 36.8911, "longitude": 127.8223, "wireless_link": { "4g_freq_band": 5.8, "4g_gnd_quality": 0, "4g_link_state": 0, "4g_quality": 0, "4g_uav_quality": 0, "dongle_number": 0, "link_workmode": 0, "sdr_freq_band": 1, "sdr_link_state": 1, "sdr_quality": 5 } }, "tid": "00000000-0000-0000-0000-000000000000", "timestamp": 1701742231501, "gateway": `${device_sn2Two}` }
    let requestPayloads6 = { "bid": "00000000-0000-0000-0000-000000000000", "data": { "event": "status_code", "method": "status_code", "output": { "codes": [{ "id": 521142273 }] } }, "tid": "00000000-0000-0000-0000-000000000000", "timestamp": 1701742231507, "gateway": `${device_sn2Two}` }
    let requestPayloads7 = { "bid": "00000000-0000-0000-0000-000000000000", "data": { "68-0-0": { "gimbal_pitch": 0, "gimbal_roll": 0, "gimbal_yaw": -125.9, "payload_index": "68-0-0", "zoom_factor": 0.56782334384858046 }, "attitude_head": 0, "attitude_pitch": -1, "attitude_roll": 0.4, "battery": { "batteries": [{ "capacity_percent": 81, "firmware_version": "08.75.02.23", "high_voltage_storage_days": 0, "index": 0, "loop_times": 150, "sn": "4ERKL1H6G30XU5", "sub_type": 0, "temperature": 37.8, "type": 0, "voltage": 16340 }], "capacity_percent": 81, "landing_power": 8, "remain_flight_time": 0, "return_home_power": 0 }, "distance_limit_status": { "distance_limit": 480, "state": 0 }, "elevation": 0, "firmware_version": "07.01.2001", "gear": 1, "height": -0.10012054443359375, "height_limit": 150, "home_distance": 0.66433465480804443, "horizontal_speed": 0, "latitude": 36.891093959338257, "longitude": 127.82229967548831, "mode_code": 0, "position_state": { "gps_number": 15, "is_fixed": 0, "quality": 5, "rtk_number": 0 }, "storage": { "total": 60096000, "used": 26204000 }, "total_flight_distance": 0, "total_flight_time": 0, "track_id": "", "vertical_speed": 0, "wind_direction": 0, "wind_speed": 0 }, "tid": "00000000-0000-0000-0000-000000000000", "timestamp": 1701742231508, "gateway": `${device_sn2Two}` }
    let requestPayloads8 = { "bid": "00000000-0000-0000-0000-000000000000", "data": { "event": "hms", "method": "hms", "output": { "codes": [] } }, "tid": "00000000-0000-0000-0000-000000000000", "timestamp": 1701742231508, "gateway": `${device_sn2Two}` }

    console.log(device_sn2, '!!!!!!!!!!!!!!!!!!!!!!')
    let subscribeTopics1 = `thing/product/${device_sn2}/osd`
    let subscribeTopics2 = `thing/product/${device_sn}/events`
    let subscribeTopics3 = `thing/product/${device_sn}/osd`
    let subscribeTopics4 = `thing/product/${device_sn}/events`

    let subscribeTopics5 = `thing/product/${device_sn2Two}/osd`
    let subscribeTopics6 = `thing/product/${device_snTwo}/events`
    let subscribeTopics7 = `thing/product/${device_snTwo}/osd`
    let subscribeTopics8 = `thing/product/${device_snTwo}/events`

    client.publish(subscribeTopics1, JSON.stringify(requestPayloads1), function (err) {
        if (!err) {
            console.log('메시지 발행 성공:', subscribeTopics1, JSON.stringify(requestPayloads1));
        } else {
            console.error('메시지 발행 실패:', err);
        }
    });
    client.publish(subscribeTopics2, JSON.stringify(requestPayloads2), function (err) {
        if (!err) {
            console.log('메시지 발행 성공:', subscribeTopics2, JSON.stringify(requestPayloads2));
        } else {
            console.error('메시지 발행 실패:', err);
        }
    });
    client.publish(subscribeTopics3, JSON.stringify(requestPayloads3), function (err) {
        if (!err) {
            console.log('메시지 발행 성공:', subscribeTopics3, JSON.stringify(requestPayloads3));
        } else {
            console.error('메시지 발행 실패:', err);
        }
    });
    client.publish(subscribeTopics4, JSON.stringify(requestPayloads4), function (err) {
        if (!err) {
            console.log('메시지 발행 성공:', subscribeTopics4, JSON.stringify(requestPayloads4));
        } else {
            console.error('메시지 발행 실패:', err);
        }
    });
    client.publish(subscribeTopics5, JSON.stringify(requestPayloads5), function (err) {
        if (!err) {
            console.log('메시지 발행 성공:', subscribeTopics5, JSON.stringify(requestPayloads5));
        } else {
            console.error('메시지 발행 실패:', err);
        }
    });
    client.publish(subscribeTopics4, JSON.stringify(requestPayloads6), function (err) {
        if (!err) {
            console.log('메시지 발행 성공:', subscribeTopics6, JSON.stringify(requestPayloads6));
        } else {
            console.error('메시지 발행 실패:', err);
        }
    });
    client.publish(subscribeTopics4, JSON.stringify(requestPayloads7), function (err) {
        if (!err) {
            console.log('메시지 발행 성공:', subscribeTopics7, JSON.stringify(requestPayloads8));
        } else {
            console.error('메시지 발행 실패:', err);
        }
    });
    client.publish(subscribeTopics4, JSON.stringify(requestPayloads8), function (err) {
        if (!err) {
            console.log('메시지 발행 성공:', subscribeTopics8, JSON.stringify(requestPayloads8));
        } else {
            console.error('메시지 발행 실패:', err);
        }
    });

    // 추가 코드 :: mqtt 구독 MQTT_LIVE_STOP
    client.subscribe(`thing/product/${device_sn2}/services`, (err) => {
        if (!err) {
            console.log('Subscription successfull');
        } else {
            console.error('Subscription failed:', err);
        }
    });
    client.subscribe(`thing/product/${device_sn2Two}/services`, (err) => {
        if (!err) {
            console.log('Subscription successfull');
        } else {
            console.error('Subscription failed:', err);
        }
    });

    // 2단계 : 이걸 보내야 backend에서 WS_CONFIG.deviceList 에 값이 설정되면서 다음 단계 동작이 이루어진다.
    // - 이 메시지를 보내면, ws으로 json.biz_code => 'device_online', 'device_update_topo' 가  수신된다.
    // backend에서 먼가 중요한 작업을 한다...
    // drone_device_info 테이블에 gateway_sn (5YSZL260021E9E) 가 등록되어 있지 않으면, 새로 넣고 무언가 많은 일을 한다..

    // 추가 코드 :: mqtt 발행 // 이코드도 드론 필수
    client.publish(`sys/product/${device_sn2}/status`,
        JSON.stringify({
            "tid": "53cae1b6-3ba0-2781-2522-a497d43d731a", "bid": "cb3fdd7d-4b70-255b-2259-4a0483a90e27", "timestamp": 1702277809125, "method": "update_topo",
            "data": {
                "domain": 2, "type": 144, "sub_type": 0, "device_secret": "a21b05fd8a56a5b46e685e15ab8a98a0", "nonce": "269aefe80796dd5d88df37fca4cd8e6e", "version": 1,
                "sub_devices": [{ "sn": `${device_sn}`, "domain": 0, "type": 77, "sub_type": 2, "index": "A", "device_secret": "b7bc6c63e86c377abbf83997baf44b29", "nonce": "f6369d34b8076b8f7b3faeca93731cc6", "version": 1 }]
            }
        }),
        function (err) {
            if (!err) {
                console.log('Message published successfully');
            } else {
                console.error('Error publishing message:', err);
            }
        }
    );
    client.publish(`sys/product/${device_sn2Two}/status`,
        JSON.stringify({
            "tid": "53cae1b6-3ba0-2781-2522-a497d43d731a", "bid": "cb3fdd7d-4b70-255b-2259-4a0483a90e27", "timestamp": 1702277809125, "method": "update_topo",
            "data": {
                "domain": 2, "type": 144, "sub_type": 0, "device_secret": "a21b05fd8a56a5b46e685e15ab8a98a0", "nonce": "269aefe80796dd5d88df37fca4cd8e6e", "version": 1,
                "sub_devices": [{ "sn": `${device_snTwo}`, "domain": 0, "type": 77, "sub_type": 2, "index": "A", "device_secret": "b7bc6c63e86c377abbf83997baf44b29", "nonce": "f6369d34b8076b8f7b3faeca93731cc6", "version": 1 }]
            }
        }),
        function (err) {
            if (!err) {
                console.log('Message published successfully');
            } else {
                console.error('Error publishing message:', err);
            }
        }
    );
}


// document.getElementById("connectButton").addEventListener("click", onConnectClick);     // 연결(로그인 + ??)
document.getElementById("resetButton").addEventListener("click", onResetClick);         // 로그 지움
document.getElementById("websocketButton").addEventListener("click", onWebsocketClick); // 로그인 + 웹소켓 연결
document.getElementById("mqttButton").addEventListener("click", onMqttClick);           // mqtt 연결
document.getElementById("eastButton").addEventListener("click", onEastClick);           // 동 이동
document.getElementById("westButton").addEventListener("click", onWestClick);           // 서 이동
document.getElementById("southButton").addEventListener("click", onSouthClick);         // 남 이동
document.getElementById("northButton").addEventListener("click", onNorthClick);         // 북 이동
document.getElementById("stopButton").addEventListener("click", onStopClick);           // 멈춤
document.getElementById("playButton").addEventListener("click", onPlayClick);           // 플레이
document.getElementById("topButton").addEventListener("click", onTopClick);           // 고도 위
document.getElementById("bottomButton").addEventListener("click", onBottomClick);           // 고도 아래