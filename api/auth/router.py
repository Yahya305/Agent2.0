from fastapi import APIRouter, Depends, HTTPException, status

auth_router = APIRouter(
    prefix="/auth",          # All routes start with /auth
    tags=["Auth"],           # OpenAPI docs group name
)

@auth_router.post("/login")
async def login(username: str, password: str):
    if username == "admin" and password == "secret":
        return {"message": "Login successful"}
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

@auth_router.post("/register")
async def register(username: str, password: str):
    # In real app, save user to DB
    return {"message": f"User {username} registered successfully"}
