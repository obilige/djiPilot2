from fastapi import APIRouter, Depends, HTTPException
from .utility.db import postgres as db
import json

router = APIRouter(
    prefix="/back/map/api/v1",
    tags=["map"]
)

emqx = "emqx-broker:8083"
workspace_id = "e3dea0f5-37f2-4d79-ae58-490af3228069" #uuid string으로 들어가야 리모트 컨트롤러 클라우드 로그인이 물림
workspace_name = "Sinto-Mavic3M"
user_id = "be7c6c3d-afe9-4be4-b9eb-c55066c0914e"


@router.get("/")
def hello():
    result = {"code": 0, "message": "connection to map is success", "data":""}
    return result
