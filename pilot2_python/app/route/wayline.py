from fastapi import APIRouter, File, Form, UploadFile, Depends, HTTPException
from typing import Annotated
from ..dependencies import get_token_header
import os

from utility.postgres import postgres as db

import uuid
import zipfile # kmz 파일 압축풀기 위한 모듈 사용
import xmltodict # wayline 파일은 xml 형식. 데이터 읽기 위해 dict로 변환해주는 모듈 사용
import json # xmltodict를 바로 사용하면 안에 리스트 담겨서 나옴. json 모양으로 바꿔주기 위해 json으로 dumps, load 2단계 거치려고 사용

router = APIRouter(
    prefix="/back/wayline/api/v1",
    tags=["wayline"],
    dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)

path = "/home/app/"

@router.get("/")
async def hello():
    result = {"code": 0, "message": "connection success", "data":""}
    return result


@router.post('/workspaces/{workspace_id}/waylines/file/upload')
async def upload_wayline_file(file: Annotated[bytes, File()],
    fileb: Annotated[UploadFile, File()],
    token: Annotated[str, Form()],
    workspace_id):
    """
    1. 경로파일 업로드
    2. OSS or No OSS ?  No OSS로 구현
    3. 관리자 웹페이지에서 kmz 파일을 업로드할 때 사용
    """
    try:
        # wayline 파일 담아둘 디렉토리 생성
        if not await os.path.exists(path):
            os.makedirs(path) # 경로에 대한건 좀 더 고민해보기

        # 변수 지정
        workspace_id = workspace_id
        wayline_id = uuid.uuid4()
        filename = file.filename
        object_key = f"wayline/{filename}" #media 파일은 media 디렉토리로 // wayline 파일은 wayline 디렉토리로 관리
        filepath = path + filename
        
        # DB에 파일 정보 등록하기 위해 필요한 정보 빼내기
        kmz_read = await zipfile.ZipFile(filepath, 'r')
        wpml = await json.load(json.dumps(xmltodict.parse(kmz_read.read('*.wpml'))))
        
        drone_model_key = wpml.drone_model_key # shape example : 0-77-2
        drone_enum_value = drone_model_key.split('-')[1]
        drone_enum_sub_value = drone_model_key.split('-')[2]
        payload_model_keys = wpml.payload_model_keys
        payload_enum_value = payload_model_keys.spilit('-')[1]
        payload_enum_sub_value = payload_model_keys.spilit('-')[2]
        template_types = wpml.templmate_types[0]
        
        # DB에 담아줄 데이터 생성하기(postgres)
        wpml_info = {}
        wp_mode = 0 if template_types == 1 else 1
        oss_path = {{'wayline_id': wayline_id, 'template_types': template_types, 'object_key': object_key, 'name': filename}}
        
        # DB에 update할지 insert할지 파악해야함
        rows = db.get_list_object_key()
        datas = [rows[i] for i in range(len(rows))]

        db.insert_wayline(wpml_info, oss_path) if oss_path in datas else db.update_wayline(wpml_info, oss_path, object_key)
        result = {"code":0, "message":"success", "data":""}
    
    except:
        result = {"code":500, "message":"Fail", "data":""}

    return result


# 여기서부터
@router.get('/workspaces/{workspace_id}/waylines')
async def waylines_data(workspace_id, order_by, page, page_size, favorited: bool = False, file_type: int = 5):
    '''
    query: ordey_by, page, page_size, file_type, favorited
    '''
    try:
        rows = await db.wayline_data()

        pagination = {
            "page": page,
            "page_size": page_size,
            "total": len(rows)
        }

        list_ = [{
            "template_types": [rows[i].template_types],
            "object_key": rows[i].object_key,
            "wayline_id": rows[i].wayline_id,
            "name": rows[i].name} for i in range(len(rows))]

        data = {"list": list_, "pagination": pagination}
        result = {"code":0, "message":"success", "data":data}
    except:
        result = {"code": 500, "message": "fail", "data":""}
    return result
    
    
    


@router.put("/{item_id}", tags=["cudstom"],responses={403: {"description": "Operation forbidden"}})
async def update_item(item_id: str):
    if item_id != "plumbus":
        raise HTTPException(
            status_code=403, detail="You can only update the item: plumbus"
        )
    return {"item_id": item_id, "name": "The great Plumbus"}