from fastapi import APIRouter, Depends, HTTPException
import os
import json
from .utility.oss import minio

router = APIRouter(
    prefix="/back/storage/api/v1",
    tags=["manage"],
    responses={404: {"description": "Not found"}},
)

config = {
    'host': os.environ['OSS_HOST'],
    'port': os.environ['OSS_PORT'],
    'bucket': os.environ['BUCKET'],
    'accesskey': os.environ['ACC_KEY'], 
    'secretkey': os.environ['SEC_KEY'],
    'region': os.environ['MINIO_REGION'],
    'dir': 'pilot2',
    'provider': 'minio',
}

@router.post('/workspaces/{workspace_id}/sts')
def remote_oss_info(workspace_id, config):
    '''
    1. 리모트 컨트롤러 oss 접속 정보 제공
    2. 외부에서 접근 가능한 정보를 제공해야함
    '''
    if minio(config):
        data = {
            "bucket": config['bucket'],
            "credentials":{
                "access_key_id": config['accesskey'],
                "access_key_secret": config['secretkey'],
                "expire":3600,
                "security_token":""
            },
        "endpoint": f"{config['host']}:{config['port']}",
        "object_key_prefix": config['dir'],
        "provider": config['provider'],
        "region": config['region']}
        
        result = {"code": 0, "message": "success", "data": data}
    
    else:
        result = {"code": 500, "message": "fail", "data": ""}
        
    return result