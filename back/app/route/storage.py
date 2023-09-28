from fastapi import APIRouter, Depends, HTTPException
import json
from .utility.oss import minio

router = APIRouter(
    prefix="/back/storage/api/v1",
    tags=["manage"],
    responses={404: {"description": "Not found"}},
)

config = {}

@router.post('/workspaces/{workspace_id}/sts')
def remote_oss_info(workspace_id):
    '''
    1. 리모트 컨트롤러 oss 접속 정보 제공
    2. 외부에서 접근 가능한 정보를 제공해야함
    '''
    if minio(config.endPoint, config.port, config.accessKey, config.secretKey, config.region, config.bucket):
        data = {
            "bucket": config.bucket,
            "credentials":{
            "access_key_id": config.accessKey,
            "access_key_secret": config.secretKey,
            "expire":3600,
            "security_token":""
            },
        "endpoint": config.devOSSRemote or f"{config.endPoint}:{config.port}",
        "object_key_prefix": config.dir,
        "provider": config.provider,
        "region": config.region}
        
        result = {"code": 0, "message": "success", "data": data}
    
    else:
        result = {"code": 500, "message": "fail", "data": ""}
        
    return result