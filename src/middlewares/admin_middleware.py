from fastapi import Depends, HTTPException, Request

async def get_current_user(request: Request):
    user = getattr(request.state, "user", None)
    print(user)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user

def require_admin(user: dict = Depends(get_current_user)):
    if not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin required")
    return user