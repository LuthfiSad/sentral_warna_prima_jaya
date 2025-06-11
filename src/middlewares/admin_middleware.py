from fastapi import Depends, HTTPException, Request

async def get_current_user(request: Request):
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user

async def mush_not_admin_have_employee(user: dict = Depends(get_current_user)):
    if user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin not allowed")
    if not user.get("karyawan_id"):
        raise HTTPException(status_code=403, detail="Employee required")
    return user

# async def get_current_user_or_none(request: Request):
#     user = getattr(request.state, "user", None)
#     print(user)
#     return user

def require_admin(user: dict = Depends(get_current_user)):
    if not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin required")
    return user