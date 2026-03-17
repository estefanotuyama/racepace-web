import os

from fastapi import APIRouter, Header, HTTPException

from backend.db.update_db import update_db

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/update")
def trigger_update(x_admin_secret: str = Header(...)):
    expected = os.environ.get("ADMIN_SECRET")
    if not expected or x_admin_secret != expected:
        raise HTTPException(status_code=403, detail="Forbidden")

    update_db()
    return {"status": "ok"}
