from fastapi import APIRouter, UploadFile, File, WebSocket, status
from fastapi.exceptions import WebSocketException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import io, os, json, subprocess
from PIL import Image
from latex2mathml.converter import convert

from utils.model_loader import processor, pix2text_model, nemeth_model, nemeth_tokenizer
from utils.latex_cleaner import clean_latex
from utils.Latex_preprocess import preprocess_latex
from utils.auth import decode_jwt_token
from utils.changes import latex_to_nemeth as manual

from models import Equation
from database import async_session

router = APIRouter()

# --- Config ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JS_PATH = os.path.join(BASE_DIR, "Latex_to_Speech.js")
STORAGE_DIR = os.path.join(BASE_DIR, "image_results")
os.makedirs(STORAGE_DIR, exist_ok=True)

# --- Helpers ---
def latex_to_mathml(latex: str) -> str:
    return convert(latex)

def mathml_to_speech_via_js(mathml: str) -> str:
    try:
        result = subprocess.run(["node", JS_PATH, mathml], capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception as e:
        print("Speech JS Exception:", e)
        return None

async def save_equation_to_db(user_id: str, latex: str, mathml: str,  nemeth: str):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(Equation).where(Equation.user_id == user_id, Equation.latex == latex)
            )
            existing = result.scalars().first()

            if existing:
                existing.mathml = mathml
                existing.nemeth = nemeth
                session.add(existing)
            else:
                equation = Equation(
                    user_id=user_id,
                    latex=latex,
                    mathml=mathml,
                    nemeth=nemeth,
                )
                session.add(equation)


# --- Pydantic ---
class ImageToNemethInput(BaseModel):
    token: str

# --- POST: Convert Image to Nemeth ---
@router.post("/")
async def image_to_nemeth(file: UploadFile = File(...), token: str = ""):
    user_id = decode_jwt_token(token)

    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")

    # Save image
    filename = f"{datetime.utcnow().isoformat().replace(':', '-')}_{file.filename}"
    image_path = os.path.join(STORAGE_DIR, filename)
    image.save(image_path)

    # 1. Extract LaTeX
    pixel_values = processor(images=image, return_tensors="pt").pixel_values
    generated_ids = pix2text_model.generate(pixel_values)
    latex = clean_latex(processor.batch_decode(generated_ids, skip_special_tokens=True)[0])

    # 2. Convert to MathML
    mathml = latex_to_mathml(latex)

    # 3. Convert to spoken text
    spoken_text = mathml_to_speech_via_js(mathml)

    # 4. Convert to Nemeth
    cleaned = f"latex2nemeth:{preprocess_latex(latex)}"
    inputs = nemeth_tokenizer(cleaned, return_tensors="pt").to(nemeth_model.device)
    nemeth_ids = nemeth_model.generate(**inputs, max_new_tokens=128, num_beams=4, early_stopping=True)
    nemeth = nemeth_tokenizer.decode(nemeth_ids[0], skip_special_tokens=True)

    # Save results
    await save_equation_to_db(user_id, latex, mathml, spoken_text, nemeth)

    return {
        "latex": latex,
        "mathml": mathml,
        "spoken_text": spoken_text,
        "nemeth": nemeth
    }

# --- WebSocket: LaTeX to Nemeth ---


@router.websocket("/ws/latex-nemeth")
async def websocket_latex_to_nemeth(websocket: WebSocket):
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

            latex = message.get("latex")
            if not latex:
                await websocket.send_json({"error": "No LaTeX field provided"})
                continue

            # === Model-based Nemeth Generation ===
            cleaned = f"latex2nemeth: {preprocess_latex(latex)}"
            inputs = nemeth_tokenizer(cleaned, return_tensors="pt").to(nemeth_model.device)

            nemeth_ids = nemeth_model.generate(
                **inputs, max_new_tokens=128, num_beams=4, early_stopping=True
            )
            model_nemeth = nemeth_tokenizer.decode(nemeth_ids[0], skip_special_tokens=True)

            # === MathML and Speech ===
            mathml = latex_to_mathml(latex)
            spoken_text = mathml_to_speech_via_js(mathml)

            # === Hidden Manual Comparison (Backend Only) ===
            try:
                print(cleaned)
                man_nemeth = manual(cleaned)
                if man_nemeth.strip() != model_nemeth.strip():
                    model_nemeth= man_nemeth
                    print(f"Generated")
            except Exception as e:
                print(f"[Manual Nemeth Error] {e}")

            # === Save and Respond ===
            await save_equation_to_db(user_id, latex, mathml, model_nemeth)

            await websocket.send_json({
                "latex": latex,
                "mathml": mathml,
                "spoken_text": spoken_text,
                "nemeth": model_nemeth,
                "rendered": f"\\text{{{model_nemeth}}}"
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
