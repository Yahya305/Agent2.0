import jwt
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from api.auth.service import AuthService
from jwt import ExpiredSignatureError
from core.database import SessionLocal
from datetime import timedelta
from core.constants import ACCESS_TOKEN_EXPIRE_MINUTES, ACCESS_TOKEN_SECRET


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        # Skip unprotected routes
        if request.url.path in ["/api/auth/login", "/api/auth/register"]:
            return await call_next(request)

        access_token = request.cookies.get("access_token")

        # ✅ Open a session for this request
        db = SessionLocal()
        auth_service = AuthService(db)

        try:
            # ✅ Try normal access token verification
            user_info = auth_service.verify_access_token(access_token)
            request.state.user = user_info
            return await call_next(request)

        except ExpiredSignatureError:
            # ✅ Decode expired token to extract user_id
            try:
                payload = jwt.decode(
                    access_token,
                    ACCESS_TOKEN_SECRET,
                    algorithms=["HS256"],
                    options={"verify_exp": False},  # ignore expiration
                )
                user_id = payload.get("userId")
                print("User ID from expired token:", user_id)
            except Exception:
                return JSONResponse({"detail": "Unauthorized"}, status_code=401)

            # ✅ Fetch refresh session for this user
            session = auth_service.fetch_user_session(user_id)
            if not session:
                return JSONResponse({"detail": "Unauthorized"}, status_code=401)

            refresh_token = session.refresh_token
            refreshed_session = auth_service.verify_refresh_token(refresh_token)

            if refreshed_session:
                new_access_token = auth_service.create_access_token(refreshed_session.user)
                request.state.user = {
                    "userId": str(refreshed_session.user.id),
                    "username": refreshed_session.user.username,
                    "email": refreshed_session.user.email,
                }

                # Get downstream response
                response = await call_next(request)

                # ✅ Set new access token cookie
                response.set_cookie(
                    "access_token",
                    new_access_token,
                    httponly=True,
                    max_age=int(timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES).total_seconds()),
                )
                return response

            return JSONResponse({"detail": "Unauthorized"}, status_code=401)

        except Exception:
            return JSONResponse({"detail": "Unauthorized"}, status_code=401)

        finally:
            # ✅ Always close DB session
            db.close()
