from fastapi import APIRouter, Depends, HTTPException
from ..dependencies import get_token_header

router = APIRouter(
    prefix="/back/manage/api/v1",
    tags=["manage"],
    dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)



@router.get("/")
async def hello():
    result = {"code": 0, "message": "connection to manage is success", "data":""}
    return result

@router.post("/login")
async def login(item):
    result = {"code": 0, "message": "connection success", "data":""}
    return result

@router.put("/{item_id}", tags=["custom"],responses={403: {"description": "Operation forbidden"}})
async def update_item(item_id: str):
    if item_id != "plumbus":
        raise HTTPException(
            status_code=403, detail="You can only update the item: plumbus"
        )
    return {"item_id": item_id, "name": "The great Plumbus"}