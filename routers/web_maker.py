from fastapi import APIRouter
from fastapi.responses import RedirectResponse


router = APIRouter(prefix="/maker", tags=["Web Maker"])


@router.get("/faysal")
def maker_info():
    return RedirectResponse(url="https://faysalmahmudsajan.github.io/")
