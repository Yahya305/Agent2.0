
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from api.auth.service import AuthService
from jwt import ExpiredSignatureError

class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, auth_service: AuthService):
        super().__init__(app)
        self.auth_service = auth_service

    async def dispatch(self, request: Request, call_next):
        # Skip unprotected routes
        if request.url.path in ["/api/auth/login", "/api/auth/register"]:
            return await call_next(request)

        access_token = request.cookies.get("access_token")
        refresh_token = request.cookies.get("refresh_token")

        try:
            user_info = self.auth_service.verify_access_token(access_token)
            request.state.user = user_info
            return await call_next(request)
        except ExpiredSignatureError:
            # Try refreshing
            session = self.auth_service.verify_refresh_token(refresh_token)
            if session:
                new_access_token = self.auth_service.create_access_token(session.user)
                request.state.user = {"userId": session.user.id, "username": session.user.username, "email": session.user.email}
                response = await call_next(request)
                response.set_cookie("access_token", new_access_token, httponly=True, max_age=...)
                return response
            return JSONResponse({"detail": "Unauthorized"}, status_code=401)
        except Exception:
            return JSONResponse({"detail": "Unauthorized"}, status_code=401)
