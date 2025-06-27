from fastapi import APIRouter, UploadFile, File, WebSocket, status
from jose import JWTError, jwt
from pydantic import BaseModel
from utils.model_loader import processor, pix2text_model, nemeth_model, nemeth_tokenizer
from utils.latex_cleaner import clean_latex
from utils.Latex_preprocess import preprocess_latex
from PIL import Image
import io
import torch
import subprocess
import os
import json
from datetime import datetime
import base64
from latex2mathml.converter import convert
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
        if not user_id:
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="user_id not found in token")
        return user_id
    except JWTError:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")

def latex_to_mathml(latex: str) -> str:
    return convert(latex)

def mathml_to_speech_via_js(mathml: str) -> str:
    try:
        result = subprocess.run(["node", JS_PATH, mathml], capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception as e:
        print("Speech JS Exception:", e)
        return None

async def save_equation_to_db(user_id: str, latex: str, mathml: str, spoken_text: str, nemeth: str):
    async with async_session() as session:
        async with session.begin():
            equation = Equation(
                user_id=user_id,
                latex=latex,
                mathml=mathml,
                spoken_text=spoken_text,
                nemeth=nemeth
            )
            session.add(equation)
        await session.commit()

# --- Request Schema ---
class ImageToNemethInput(BaseModel):
    token: str

# --- REST API Route ---
@router.post("/")
async def image_to_nemeth(file: UploadFile = File(...), token: str = ""):
    user_id = decode_jwt_token(token)

    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")

    # Save image
    filename = f"{datetime.utcnow().isoformat().replace(':', '-')}_{file.filename}"
    image_path = os.path.join(STORAGE_DIR, filename)
    image.save(image_path)

    # 1. LaTeX
    pixel_values = processor(images=image, return_tensors="pt").pixel_values
    generated_ids = pix2text_model.generate(pixel_values)
    latex = clean_latex(processor.batch_decode(generated_ids, skip_special_tokens=True)[0])

    # 2. MathML
    mathml = latex_to_mathml(latex)

    # 3. Spoken text
    spoken_text = mathml_to_speech_via_js(mathml)

    # 4. Nemeth
    cleaned = preprocess_latex(latex)
    inputs = nemeth_tokenizer(cleaned, return_tensors="pt").to(nemeth_model.device)
    nemeth_ids = nemeth_model.generate(**inputs, max_length=512)
    nemeth = nemeth_tokenizer.decode(nemeth_ids[0], skip_special_tokens=True)

    # Save result
    await save_equation_to_db(user_id, latex, mathml, spoken_text, nemeth)

    return {
        "latex": latex,
        "mathml": mathml,
        "spoken_text": spoken_text,
        "nemeth": nemeth
    }

# --- WebSocket Route ---
@router.websocket("/ws/latex-nemeth")
async def websocket_image_to_nemeth(websocket: WebSocket):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    try:
        user_id = decode_jwt_token(token)
    except WebSocketException:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            base64_str = message.get("image")
            if not base64_str:
                await websocket.send_json({"error": "No image field provided"})
                continue

            image_data = base64.b64decode(base64_str)
            image = Image.open(io.BytesIO(image_data)).convert("RGB")

            pixel_values = processor(images=image, return_tensors="pt").pixel_values
            generated_ids = pix2text_model.generate(pixel_values)
            latex = clean_latex(processor.batch_decode(generated_ids, skip_special_tokens=True)[0])
            mathml = latex_to_mathml(latex)
            spoken_text = mathml_to_speech_via_js(mathml)

            cleaned = preprocess_latex(latex)
            inputs = nemeth_tokenizer(cleaned, return_tensors="pt").to(nemeth_model.device)
            nemeth_ids = nemeth_model.generate(**inputs, max_length=512)
            nemeth = nemeth_tokenizer.decode(nemeth_ids[0], skip_special_tokens=True)

            await save_equation_to_db(user_id, latex, mathml, spoken_text, nemeth)

            await websocket.send_json({
                "latex": latex,
                "mathml": mathml,
                "spoken_text": spoken_text,
                "nemeth": nemeth
            })

    except Exception as e:
        try:
            await websocket.send_json({"error": str(e)})
        except:
            pass
        finally:
            try:
                await websocket.close()
            except:
                pass
