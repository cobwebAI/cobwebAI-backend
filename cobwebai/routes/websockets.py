from typing import TypedDict
import socketio
import jwt

from cobwebai.utils.log import logger
from cobwebai.utils.auth import settings


class UserSession(TypedDict):
    user_id: str


def validate_access_token(access_token: str) -> str | None:
    try:
        payload = jwt.decode(access_token, settings.users_secret, algorithms=["HS256"])
        return payload.get("sub")
    except jwt.InvalidTokenError:
        return None


class OperationsNamespace(socketio.AsyncNamespace):
    async def on_connect(self, sid, environ, auth):
        if not isinstance(auth, dict):
            await self.disconnect(sid)
            return

        access_token = auth.get("token")
        if access_token is None:
            await self.disconnect(sid)
            return

        user_id = validate_access_token(access_token)
        if user_id is None:
            await self.disconnect(sid)
            return

        logger.info(f"User {user_id} connected to operations namespace")

        await self.save_session(sid, {"user_id": user_id})
        await self.enter_room(sid, f"operations_{user_id}")
