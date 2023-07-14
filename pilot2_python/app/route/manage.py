from fastapi import APIRouter, Depends, HTTPException
from ..dependencies import get_token_header
from utility.postgres import postgres  as db
import json

router = APIRouter(
    prefix="/back/manage/api/v1",
    tags=["manage"],
    dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)

emqx = "emqx-broker:8083"
workspace_id = "e3dea0f5-37f2-4d79-ae58-490af3228069" #uuid string으로 들어가야 리모트 컨트롤러 클라우드 로그인이 물림
workspace_name = "Sinto-Mavic3M"
user_id = "be7c6c3d-afe9-4be4-b9eb-c55066c0914e"


@router.get("/")
async def hello():
    result = {"code": 0, "message": "connection to manage is success", "data":""}
    return result


@router.post("/login")
async def login(item):
    info = item.dict()
    id = info.username
    password = info.password
    flag = info.flag
    row = await db.login(id)

    if row.account_id == False or row.account_id != id: 
        result = {} # fail
    elif row.password != password:
        result = {} # fail
    else:
        # for test
        data = {
        "username": row.account_id,
        "user_id": user_id,
        "workspace_id": workspace_id,
        "user_type": int(flag),
        "mqtt_username": "pilot",
        "mqtt_password": "pilot123",
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ3b3Jrc3BhY2VfaWQiOiJlM2RlYTBmNS0zN2YyLTRkNzktYWU1OC00OTBhZjMyMjgwNjkiLCJzdWIiOiJDbG91ZEFwaVNhbXBsZSIsInVzZXJfdHlwZSI6IjEiLCJuYmYiOjE2ODQyOTgxMDIsImxvZyI6IkxvZ2dlcltjb20uZGppLnNhbXBsZS5jb21tb24ubW9kZWwuQ3VzdG9tQ2xhaW1dIiwiaXNzIjoiREpJIiwiaWQiOiJhMTU1OWU3Yy04ZGQ4LTQ3ODAtYjk1Mi0xMDBjYzQ3OTdkYTIiLCJleHAiOjE3NzA2OTgxMDIsImlhdCI6MTY4NDI5ODEwMiwidXNlcm5hbWUiOiJhZG1pblBDIn0.Ya3PDqZRS-arhy1a-5wi8kiWcDwuy6DZNsI_uTy_03c",
        "mqtt_addr": emqx
        }
        result = {"code": 0, "message": "success", "data": data} # success
    return json.load(result)


@router.get('/workspaces/current')
def current_data():
    data = db.current_data()
    result = {"code": 0, "message": "success", "data": data}
    return json.load(result)

@router.get('/users/current')
def user_data():
    data = db.user_data()
    result = {"code": 0, "message": "success", "data": data}
    return json.load(result)

# 샘플 프론트 화면에서 장비 리스트를 표출하기 위해 데이터 요청
@router.get('/devices/{workspace_id}/devices/bound')
def device_bound(workspace_id):
    data = {
    "list": [
        {
          "device_sn": "1581F5FKD232800D2TK8",
          "device_name": "Mavic 3M",
          "workspace_id": f"{workspace_id}",
          "device_index": "A",
          "device_desc": "",
          "child_device_sn": "",
          "domain": 0,
          "type": 77,
          "sub_type": 2,
          "icon_url": {
            "normal_icon_url": "resource://pilot/drawable/tsa_person_normal",
            "selected_icon_url": "resource://pilot/drawable/tsa_person_select"
          },
          "status": True,
          "bound_status": True,
          "login_time": "2023-04-27 08:39:40",
          "bound_time": "2023-04-20 02:28:12",
          "nickname": "Mavic 3M",
          "firmware_version": "06.01.0606",
          "workspace_name": "Test Group One",
          "firmware_status": 1
        },
        {
          "device_sn": "1ZNBJAA0HC0001",
          "device_name": "Matrice 300",
          "workspace_id": f"{workspace_id}",
          "device_index": "A",
          "device_desc": "",
          "child_device_sn": "",
          "domain": 0,
          "type": 77,
          "sub_type": 2,
          "icon_url": {
            "normal_icon_url": "resource://pilot/drawable/tsa_person_normal",
            "selected_icon_url": "resource://pilot/drawable/tsa_person_select"
          },
          "status": True,
          "bound_status": True,
          "login_time": "2023-04-27 08:39:40",
          "bound_time": "2023-04-20 02:28:12",
          "nickname": "Matrice 300",
          "firmware_version": "06.01.0606",
          "workspace_name": "Test Group One",
          "firmware_status": 1
        }
      ]
    }
    result = {"code": 0, "message": "success", "data": data}
    return json.load(result)

@router.get('/devices/{workspace_id}/devices')
async def device_list(workspace_id):
    data = [
      {
        "device_sn": "5YSZL260021E9E",
        "device_name": "DJI RC Pro",
        "workspace_id": f"{workspace_id}",
        "device_index": "",
        "device_desc": "Remote control for Mavic 3E/T and Mavic 3M",
        "child_device_sn": "1581F5FKD232800D2TK8",
        "domain": 2,
        "type": 144,
        "sub_type": 0,
        "icon_url": {
          "normal_icon_url": "resource://pilot/drawable/tsa_person_normal",
          "selected_icon_url": "resource://pilot/drawable/tsa_person_select"
        },
        "bound_status": True,
        "status": True,
        "children": {
          "device_sn": "1581F5FKD232800D2TK8",
          "device_name": "Mavic 3M",
          "workspace_id": f"{workspace_id}",
          "device_index": "A",
          "device_desc": "",
          "child_device_sn": "",
          "domain": 0,
          "type": 77,
          "sub_type": 2,
          "payloads_list": [
            {
              "payload_sn":"1581F5FKD232800D2TK8-0",
              "payload_name":"Mavic 3M Camera",
              "payload_index":0
            }
          ],
          "icon_url":{
            "normal_icon_url":"resource://pilot/drawable/tsa_person_normal",
            "selected_icon_url":"resource://pilot/drawable/tsa_person_select"
          },
          "status":True,
          "bound_status":True,
          "login_time":"2023-05-12 00:21:41",
          "bound_time":"2023-04-20 02:28:12",
          "nickname":"Mavic 3M",
          "firmware_version":"06.01.0606",
          "workspace_name":"Test Group One",
          "firmware_status":1
        },
        "login_time": "2023-05-03 04:16:41",
        "bound_time": "2023-05-03 02:18:41",
        "nickname": "DJI RC Pro",
        "firmware_version": "02.00.0407",
        "workspace_name": "Test Group One",
        "firmware_status": 1
      },
      {
        "device_sn": "5EKBJ9U001000N",
        "device_name": "DJI Matrice 300",
        "workspace_id": f"{workspace_id}",
        "device_index": "",
        "device_desc": "Remote control for Mavic 3E/T and Matrice 300",
        "child_device_sn": "1ZNBJAA0HC0001",
        "domain": 2,
        "type": 56,
        "sub_type": 0,
        "icon_url": {
          "normal_icon_url": "resource://pilot/drawable/tsa_person_normal",
          "selected_icon_url": "resource://pilot/drawable/tsa_person_select"
        },
        "bound_status": True,
        "status": True,
        "children": {
          "device_sn": "1ZNBJAA0HC0001",
          "device_name": "Matrice 300",
          "workspace_id": f"{workspace_id}",
          "device_index": "A",
          "device_desc": "",
          "child_device_sn": "",
          "domain": 0,
          "type": 77,
          "sub_type": 2,
          "payloads_list":[
            {
              "payload_sn":"1ZNBJAA0HC0001-0",
              "payload_name":"Matrice 300 Camera",
              "payload_index":0
            }
          ],
          "icon_url":{
            "normal_icon_url":"resource://pilot/drawable/tsa_person_normal",
            "selected_icon_url":"resource://pilot/drawable/tsa_person_select"
          },
          "status":True,
          "bound_status":True,
          "login_time":"2023-05-12 00:21:41",
          "bound_time":"2023-04-20 02:28:12",
          "nickname":"Matrice 300",
          "firmware_version":"06.01.0606",
          "workspace_name":"Test Group One",
          "firmware_status":1
        },
        "login_time": "2023-05-03 04:16:41",
        "bound_time": "2023-05-03 02:18:41",
        "nickname": "DJI Matrice 300",
        "firmware_version": "02.00.0407",
        "workspace_name": "Test Group One",
        "firmware_status": 1
      }
    ]
    result = {"code": 0, "message": "success", "data": data}
    return json.load(result)

@router.get('/devices/:workspace_id/devices/:device_sn')
def device_sn(workspace_id, device_sn):
    if device_sn == "5YSZL260021E9E":
        result = {"code":0,"message":"success","data":{"device_sn":device_sn,"device_name":"DJI RC Pro","workspace_id":f"{workspace_id}","device_index":"","device_desc":"Remote control for Mavic 3E/T and Mavic 3M","child_device_sn":"1581F5FKD232800D2TK8","domain":2,"type":144,"sub_type":0,"icon_url":{"normal_icon_url":"resource://pilot/drawable/tsa_person_normal","selected_icon_url":"resource://pilot/drawable/tsa_person_select"},"status":True,"bound_status":True,"login_time":"2023-05-15 05:17:01","bound_time":"2023-05-15 05:17:01","nickname":"DJI RC Pro","firmware_version":"02.00.0407","workspace_name":"Test Group One","firmware_status":1}}
    elif device_sn == "1581F5FKD232800D2TK8":
        result = {"code":0,"message":"success","data":{"device_sn":device_sn,"device_name":"Mavic 3M","workspace_id":f"{workspace_id}","device_index":"A","device_desc":"","child_device_sn":"","domain":0,"type":77,"sub_type":2,"icon_url":{"normal_icon_url":"resource://pilot/drawable/tsa_person_normal","selected_icon_url":"resource://pilot/drawable/tsa_person_select"},"status":True,"bound_status":True,"login_time":"2023-05-15 05:17:01","bound_time":"2023-04-21 08:06:22","nickname":"Mavic 3M","firmware_version":"06.01.0606","workspace_name":"Test Group One","firmware_status":1}}
    elif device_sn == "5EKBJ9U001000N":
        result = {"code":0,"message":"success","data":{"device_sn":device_sn,"device_name":"DJI Matrice 300","workspace_id":f"{workspace_id}","device_index":"","device_desc":"Remote control for Mavic 3E/T and Matrice 300","child_device_sn":"1ZNBJAA0HC0001","domain":2,"type":144,"sub_type":0,"icon_url":{"normal_icon_url":"resource://pilot/drawable/tsa_person_normal","selected_icon_url":"resource://pilot/drawable/tsa_person_select"},"status":True,"bound_status":True,"login_time":"2023-05-15 05:17:01","bound_time":"2023-05-15 05:17:01","nickname":"DJI RC Pro","firmware_version":"02.00.0407","workspace_name":"Test Group One","firmware_status":1}}
    elif device_sn == "1ZNBJAA0HC0001":
        result = {"code":0,"message":"success","data":{"device_sn":device_sn,"device_name":"Matrice 300","workspace_id":f"{workspace_id}","device_index":"A","device_desc":"","child_device_sn":"","domain":0,"type":77,"sub_type":2,"icon_url":{"normal_icon_url":"resource://pilot/drawable/tsa_person_normal","selected_icon_url":"resource://pilot/drawable/tsa_person_select"},"status":True,"bound_status":True,"login_time":"2023-05-15 05:17:01","bound_time":"2023-04-21 08:06:22","nickname":"Matrice 300","firmware_version":"06.01.0606","workspace_name":"Test Group One","firmware_status":1}}
    return result

@router.post('/token/refresh')
def token_refresh(item):
    # post로 담겨오는 데이터 뭔지 확인 후 프론트에 쏴줄 데이터 생성
    print(f"[token_refresh] {item}")
    data = {
      "mqtt_addr": emqx,
      "mqtt_username": "pilot",
      "mqtt_password": "pilot123",
      "username": f"{item.username}",
      "user_id": user_id,
      "workspace_id": workspace_id,
      "user_type": 2,
      "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ3b3Jrc3BhY2VfaWQiOiJlM2RlYTBmNS0zN2YyLTRkNzktYWU1OC00OTBhZjMyMjgwNjkiLCJzdWIiOiJDbG91ZEFwaVNhbXBsZSIsInVzZXJfdHlwZSI6IjEiLCJuYmYiOjE2ODQyOTgxMDIsImxvZyI6IkxvZ2dlcltjb20uZGppLnNhbXBsZS5jb21tb24ubW9kZWwuQ3VzdG9tQ2xhaW1dIiwiaXNzIjoiREpJIiwiaWQiOiJhMTU1OWU3Yy04ZGQ4LTQ3ODAtYjk1Mi0xMDBjYzQ3OTdkYTIiLCJleHAiOjE3NzA2OTgxMDIsImlhdCI6MTY4NDI5ODEwMiwidXNlcm5hbWUiOiJhZG1pblBDIn0.Ya3PDqZRS-arhy1a-5wi8kiWcDwuy6DZNsI_uTy_03c"
    }
    result = {"code": 0, "message": "success", "data": data}
    return json.load(result)

@router.post('/devices/:device_sn/binding')

@router.put("/{item_id}", tags=["custom"],responses={403: {"description": "Operation forbidden"}})
async def update_item(item_id: str):
    if item_id != "plumbus":
        raise HTTPException(
            status_code=403, detail="You can only update the item: plumbus"
        )
    return {"item_id": item_id, "name": "The great Plumbus"}