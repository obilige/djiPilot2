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

emqx_address = "emqx-broker:8083"
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
        "mqtt_addr": emqx_address
        }
        result = {"code": 0, "message": "success", "data": data} # success
    return json.load(result)


@router.get('/workspaces/current')
def current_data():
    data = db.current_data()
    result = {"code": 0, "message": "success", "data": data}
    return json.load(result)

# 여기까지
@router.get('/users/current')
def user_data():
    data = db.user_data()
    result = {"code": 0, "message": "success", "data": data}
    return json.load(result)


@router.put("/{item_id}", tags=["custom"],responses={403: {"description": "Operation forbidden"}})
async def update_item(item_id: str):
    if item_id != "plumbus":
        raise HTTPException(
            status_code=403, detail="You can only update the item: plumbus"
        )
    return {"item_id": item_id, "name": "The great Plumbus"}