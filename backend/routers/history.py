from fastapi import APIRouter, UploadFile, File, WebSocket, status
from jose import JWTError, jwt
from pydantic import BaseModel
from PIL import Image
import os
from sqlalchemy import select, update

from models import Equation
from database import async_session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.exceptions import WebSocketException

router = APIRouter()

# --- Constants ---
SECRET_KEY = "your-super-secret-key"
ALGORITHM = "HS256"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JS_PATH = os.path.join(BASE_DIR, "Latex_to_Speech.js")
STORAGE_DIR = os.path.join(BASE_DIR, "image_results")
os.makedirs(STORAGE_DIR, exist_ok=True)

# --- Helper Functions ---
def decode_jwt_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        print(user_id)
        if not user_id:
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="user_id not found in token")
        return user_id
    except JWTError:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")

@router.websocket("/ws/history")
async def websocket_equation_history(websocket: WebSocket):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Token missing")
        return

    try:
        user_id = decode_jwt_token(token)
    except WebSocketException:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
        return

    await websocket.accept()

    try:
        async with async_session() as session:
            async with session.begin():
                result = await session.execute(
                    select(Equation).where(Equation.user_id == user_id).order_by(Equation.created_at.desc())
                )
                equations = result.scalars().all()

                if not equations:
                    await websocket.send_json({"history": []})
                    return

                history = [
                    {
                        "id": eq.id,
                        "latex": eq.latex,
                        "mathml": eq.mathml,
                        "nemeth": eq.nemeth,
                        "timestamp": eq.created_at.isoformat() if eq.created_at else None
                    }
                    for eq in equations
                ]

                await websocket.send_json({"history": history})

    except Exception as e:
        await websocket.send_json({"error": str(e)})
    finally:
        await websocket.close()
