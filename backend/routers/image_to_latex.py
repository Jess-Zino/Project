from datetime import datetime
from fastapi import WebSocket, APIRouter, UploadFile, File, status
from fastapi.exceptions import WebSocketException
from starlette.websockets import WebSocketDisconnect
from utils.model_loader import processor, pix2text_model, nemeth_model, nemeth_tokenizer
from utils.latex_cleaner import clean_latex
from utils.Latex_preprocess import preprocess_latex
from utils.auth import decode_access_token
from latex2mathml.converter import convert
from models import Equation
from database import async_session

from PIL import Image
import io
import os
import json
import base64
import subprocess

router = APIRouter()

# Config paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JS_PATH = os.path.join(BASE_DIR, "Latex_to_Speech.js")
STORAGE_DIR = os.path.join(BASE_DIR, "image_results")
os.makedirs(STORAGE_DIR, exist_ok=True)

# --- Helper functions ---
def latex_to_mathml(latex: str) -> str:
    return convert(latex)

def mathml_to_speech_via_js(mathml: str) -> str:
    try:
        result = subprocess.run(["node", JS_PATH, mathml], capture_output=True, text=True)
        if result.returncode != 0:
            print("JS error:", result.stderr)
            return None
        return result.stdout.strip()
    except Exception as e:
        print("Speech JS Exception:", e)
        return None

async def save_equation_to_db(user_id: str, latex: str, mathml: str,  nemeth: str = None):
    async with async_session() as session:
        async with session.begin():
            equation = Equation(
                user_id=user_id,
                latex=latex,
                mathml=mathml,
                nemeth=nemeth
            )
            session.add(equation)

# --- Endpoints ---
@router.post("/latex")
async def image_to_latex(file: UploadFile = File(...)):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")

    filename = f"{datetime.utcnow().isoformat().replace(':', '-')}_{file.filename}"
    image_path = os.path.join(STORAGE_DIR, filename)
    image.save(image_path)

    pixel_values = processor(images=image, return_tensors="pt").pixel_values
    generated_ids = pix2text_model.generate(pixel_values)
    latex = clean_latex(processor.batch_decode(generated_ids, skip_special_tokens=True)[0])
    mathml = latex_to_mathml(latex)
    spoken_text = mathml_to_speech_via_js(mathml)

    metadata = {
        "filename": filename,
        "latex": latex,
        "spoken_text": spoken_text,
        "timestamp": datetime.utcnow().isoformat()
    }
    with open(os.path.join(STORAGE_DIR, filename.rsplit(".", 1)[0] + ".json"), "w") as f:
        json.dump(metadata, f, indent=4)

    return {"latex": latex, "spoken_text": spoken_text}

@router.post("/")
async def image_to_nemeth(file: UploadFile = File(...), token: str = ""):
    payload = decode_access_token(token)
    if not payload or not payload.get("sub"):
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid or missing user ID")
    user_id = payload["sub"]

    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")

    filename = f"{datetime.utcnow().isoformat().replace(':', '-')}_{file.filename}"
    image_path = os.path.join(STORAGE_DIR, filename)
    image.save(image_path)

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

    return {
        "latex": latex,
        "mathml": mathml,
        "spoken_text": spoken_text,
        "nemeth": nemeth
    }

@router.websocket("/ws/image-to-latex")
async def websocket_image_to_latex(websocket: WebSocket):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    payload = decode_access_token(token)
    if not payload or not payload.get("sub"):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    user_id = payload["sub"]

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

            await save_equation_to_db(user_id, latex, mathml)

            await websocket.send_json({
                "latex": latex,
                "mathml": mathml,
                "spoken_text": spoken_text,
                "nemeth": ""
            })

    except WebSocketDisconnect:
        print("WebSocket disconnected")
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
