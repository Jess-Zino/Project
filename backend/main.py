from fastapi import FastAPI, UploadFile, File, WebSocket
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocketDisconnect
from PIL import Image
import io
import base64
import uuid
import json
import nest_asyncio
import uvicorn
from latex2mathml.converter import convert
from transformers import TrOCRProcessor
from optimum.onnxruntime import ORTModelForVision2Seq
import onnxruntime as ort
import re
import torch
import numpy as np
import os
import uuid
import subprocess
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, TrOCRProcessor

# 📦 Load model and processor from local directory


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

pix2text_model = ORTModelForVision2Seq.from_pretrained(
    "./pix2text-mfr", use_cache=False
)
processor = TrOCRProcessor.from_pretrained("./pix2text-mfr")

nemeth_model_path = "latex_to_nemeth_model_final"
nemeth_model = AutoModelForSeq2SeqLM.from_pretrained(
    nemeth_model_path, local_files_only=True
).to(device)
nemeth_tokenizer = AutoTokenizer.from_pretrained(
    nemeth_model_path, local_files_only=True
)

# ✨ Clean LaTeX output
import re


def clean_latex(latex_str):
    # Custom replacements
    latex_str = latex_str.replace("^ { 0 } / 。", "%")
    latex_str = latex_str.replace("^ { 0 } / _ { 0 }", "%")
    latex_str = latex_str.replace("。", ".")

    # Normalize whitespace
    latex_str = re.sub(r"\s+", " ", latex_str).strip()

    # Clean up \operatorname
    latex_str = re.sub(
        r"\\operatorname\*?\s*\{\s*([a-zA-Z\s]+?)\s*\}",
        lambda m: "\\operatorname*{" + m.group(1).replace(" ", "") + "}",
        latex_str,
    )
    latex_str = re.sub(
        r"\\operatorname\*?\s*\{\s*([a-zA-Z]+)\s*\}",
        lambda m: "\\" + m.group(1),
        latex_str,
    )

    # Fix exponent and subscript spacing
    latex_str = re.sub(r"([a-zA-Z0-9])([\^_])", r"\1\2", latex_str)

    # Fix decimals
    latex_str = re.sub(r"(\d)\s*\.\s*(\d)", r"\1.\2", latex_str)
    latex_str = re.sub(r"(?<!\d)\.\s*(\d+)", r".\1", latex_str)

    # Convert fractions like 5/4 into \frac{5}{4}
    # Ensures it's not already inside a \frac
    latex_str = re.sub(
        r"(?<!\\frac\{)(?<![a-zA-Z0-9])(\d+)\s*/\s*(\d+)(?!\})",
        r"\\frac{\1}{\2}",
        latex_str,
    )

    return latex_str


def preprocess_latex(latex_str):
    """Cleans and standardizes LaTeX expressions before conversion."""
    latex_str = latex_str.replace("^ { 0 } / 。", "%")
    latex_str = latex_str.replace("^ { 0 } / _ { 0 }", "%")

    latex_str = latex_str.replace("。", ".")
    # Basic cleanup (removes excessive spaces and strips any unwanted extra spaces)
    latex_str = re.sub(r"\s+", " ", latex_str).strip()

    # Remove spaces inside \operatorname and \operatorname* to avoid parsing issues
    latex_str = re.sub(
        r"\\operatorname\*?\s*\{\s*([a-zA-Z\s]+?)\s*\}",
        lambda m: "\\operatorname*{" + m.group(1).replace(" ", "") + "}",
        latex_str,
    )

    # Handle \underset { x \to 0 } { \lim }
    latex_str = re.sub(
        r"\\underset\s*\{\s*([^{}]+?)\s*\}\s*\{\s*(\\lim)\s*\}",
        r"\\lim_{\1}",  # Replace with \lim_{x \to 0}
        latex_str,
    )

    # Handle \underset { x \to 0 } { \operatorname* { l i m } }
    latex_str = re.sub(
        r"\\underset\s*\{\s*([^{}]+?)\s*\}\s*{\\operatorname\*\{\s*([^{}]+?)\s*\}}",
        r"\\lim_{\1}",  # Replace with \lim_{x \to 0}
        latex_str,
    )

    # Handle \operatorname* and \operatorname and remove spaces inside operators
    latex_str = re.sub(
        r"\\operatorname\*?\s*\{\s*([a-zA-Z]+)\s*\}",
        lambda m: "\\" + m.group(1),  # Converts \operatorname{cos} -> \cos
        latex_str,
    )
    latex_str = re.sub(
        r"(\d+)\s*\\frac\s*\{\s*([^{}]+?)\s*\}\s*\{\s*([^{}]+?)\s*\}",
        r"\1 \\mixedfrac-b \2 \\frac-separator \3 \\mixedfrac-e",
        latex_str,
    )
    latex_str = re.sub(
        r"(\d+)\s*\\frac\s*\{\s*([^{}]+?)\s*\}\s*\{\s*([^{}]+?)\s*\}",
        r"\1 \\mixedfrac-b \2 \\frac-separator \3 \\mixedfrac-e",
        latex_str,
    )
    latex_str = re.sub(
        r"(\d+)\s*\\vec\s*\{\s*([^{}]+?)\s*\}\s*\{\s*([^{}]+?)\s*\}",
        r"\1 \\mixedfrac-b \2 \\frac-separator \3 \\mixedfrac-e",
        latex_str,
    )
    # Format fractions like \frac{a}{b} (handling LaTeX math fractions)
    latex_str = re.sub(
        r"\\frac\s*\{\s*([^{}]+?)\s*\}\s*\{\s*([^{}]+?)\s*\}",
        r"\\frac-b \1 \\frac-separator \2 \\frac-e",  # Formatting fractions
        latex_str,
    )

    # Handle mixed fractions (whole number with fraction)

    latex_str = re.sub(r"\smallsetminus", r"\therefore", latex_str)

    # Handle simple array environments like \begin{array}{cc} { -1 } & {} \\ \end{array}
    latex_str = latex_str.replace(
        r"\begin{array} { c c } { - 1 } & { } \\ \end{array}", "-1"
    )

    # Remove \operatorname{...} but keep the inner content without spaces
    latex_str = re.sub(
        r"\\operatorname\s*\{\s*([\w\s]+?)\s*\}",
        lambda m: "\\" + m.group(1).replace(" ", " "),
        latex_str,
    )

    # STRIP ALL MATH FORMATTING
    latex_str = re.sub(
        r"\\(mathfrak|mathbf|mathit|mathrm|mathsf|mathtt|bf|textbf|rm|it|sf|sc|qquad|quad)\s*\{\s*([^{}]+?)\s*\}",
        r"\2",
        latex_str,
    )
    latex_str = re.sub(
        r"\{\s*\\(mathfrak|mathbf|mathit|mathrm|mathsf|mathtt|bf|textbf|rm|it|sf|sc)\s+([^{}]+?)\s*\}",
        r"\2",
        latex_str,
    )
    latex_str = re.sub(
        r"\\(mathfrak|mathbf|mathit|mathrm|mathsf|mathtt|bf|textbf|rm|it|sf|sc)\s+",
        "",
        latex_str,
    )

    # Fix exponent and subscript spacing
    latex_str = re.sub(r"([a-zA-Z0-9])([\^_])", r"\1\2", latex_str)

    # Wrap superscripts with tags: handle ^{...}
    latex_str = re.sub(
        r"\^\s*\{\s*([^{}]+?)\s*\}", r"\\superscript-b \1 \\superscript-e", latex_str
    )

    # Wrap superscripts with tags: handle ^x (no braces)
    latex_str = re.sub(
        r"\^([a-zA-Z0-9])", r"\\superscript-b \1 \\superscript-e", latex_str
    )
    latex_str = re.sub(r"\\qquad", r" ", latex_str)
    # Handle subscripts like _{...}
    latex_str = re.sub(
        r"\_\s*\{\s*([^{}]+?)\s*\}", r"\\subscript-b \1 \\subscript-e", latex_str
    )

    # Handle \sqrt[...]{...}, separating the index and base
    latex_str = re.sub(
        r"\\sqrt\s*\[(.*?)\]\s*\{(.*?)\}",
        r"\\sqrtib \1 \\sqrtie \\sqrt-b  \2 \\sqrt-e",
        latex_str,
    )

    # Handle \sqrt{...} (no index)
    latex_str = re.sub(r"\\sqrt\s*\{(.*?)\}", r"\\sqrt-b  \1 \\sqrt-e", latex_str)
    latex_str = latex_str.replace(r"\begin{array}{cc} {", "")
    latex_str = latex_str.replace(r"\begin{array} { c c } {", "")

    latex_str = latex_str.replace(r"\begin{array}{cc}", "")
    latex_str = latex_str.replace(r"\begin{array} { c c }", "")
    latex_str = latex_str.replace(r"\begin{array}{cc}{", "")
    latex_str = latex_str.replace(r"\begin{array} { c c }{", "")
    # Remove the literal \end{array}
    latex_str = latex_str.replace(r"} \\ \end{array}", "")
    # Remove the literal \end{array}
    latex_str = latex_str.replace(r"\end{array}", "")

    # Fix decimals
    latex_str = re.sub(r"(\d)\s*\.\s*(\d)", r"\1.\2", latex_str)
    latex_str = re.sub(r"(?<!\d)\.\s*(\d+)", r".\1", latex_str)

    # Merge digit groups like 1 234 -> 1234
    latex_str = re.sub(
        r"(?:\d(?: \d)+)", lambda m: m.group(0).replace(" ", ""), latex_str
    )
    # Merge digit groups like 1 234 -> 1234
    latex_str = re.sub(r"\s+", " ", latex_str).strip()

    latex_str = re.sub(r"~+", " ~ ", latex_str)

    # Remove unwanted space between digits and next character
    latex_str = re.sub(
        r"(?<=\d)\s+(?=[a-zA-Z])", " ", latex_str
    )  # only allow digit-letter merging

    # Remove \superscript-e only if it comes after \int and \superscript-b
    # Remove \subscript-e when it's directly after an \int ... \subscript-b ...
    latex_str = re.sub(
        r"(\\int(?:\\[a-z]+)*\s+\\subscript-b\s+[^\s]+)\s+\\subscript-e",
        r"\1",
        latex_str,
    )
    latex_str = re.sub(
        r"(\\int(?:\\subscript-b\s*\S+)\s*)\\subscript-e", r"\1", latex_str
    )

    return latex_str


def latex_to_mathml(latex: str) -> str:
    return convert(latex)


def mathml_to_speech_via_js(mathml: str) -> str:
    try:
        result = subprocess.run(
            ["node", "Latex_to_Speech.js", mathml], capture_output=True, text=True
        )
        if result.returncode != 0:
            print("JS error:", result.stderr)
            return None
        return result.stdout.strip()
    except Exception as e:
        print("Exception:", e)
        return None


# 🚀 FastAPI app setup
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # use specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "✅ TrOCR + Math Inference API is running."}


# 🌐 WebSocket for real-time inference
@app.websocket("/ws/img/infer")
async def websocket_infer(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Receive JSON message with base64 encoded image
            data = await websocket.receive_json()
            b64_image = data.get("image")
            if not b64_image:
                await websocket.send_json({"error": "No image data sent"})
                continue

            # Decode base64 image to PIL image
            image_bytes = base64.b64decode(b64_image)
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

            # Generate LaTeX
            pixel_values = processor(images=image, return_tensors="pt").pixel_values.to(
                device
            )
            generated_ids = pix2text_model.generate(pixel_values)
            latex = clean_latex(
                processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            )

            # Convert LaTeX to MathML and speech
            mathml = latex_to_mathml(latex)
            spoken_text = mathml_to_speech_via_js(mathml)

            # Generate Nemeth code
            input_text = f"latex2nemeth: {preprocess_latex(latex)}"
            inputs = nemeth_tokenizer(input_text, return_tensors="pt").to(device)
            nemeth_ids = nemeth_model.generate(
                **inputs, max_new_tokens=1280, num_beams=4, early_stopping=True
            )
            nemeth_output = nemeth_tokenizer.decode(
                nemeth_ids[0], skip_special_tokens=True
            )

            # Send result JSON back via websocket
            await websocket.send_json(
                {
                    "latex": latex,
                    "mathml": mathml,
                    "spoken_text": spoken_text,
                    "nemeth": nemeth_output,
                }
            )

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        await websocket.send_json({"error": str(e)})


@app.websocket("/ws/infer_text")
async def websocket_infer_text(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            latex = data.get("latex")
            if not latex:
                await websocket.send_json({"error": "No latex text sent"})
                continue

            # Convert LaTeX to MathML
            mathml = latex_to_mathml(latex)

            # Convert MathML to speech
            spoken_text = mathml_to_speech_via_js(mathml)

            # Generate Nemeth code from LaTeX
            input_text = f"latex2nemeth: {preprocess_latex(latex)}"
            inputs = nemeth_tokenizer(input_text, return_tensors="pt").to(device)
            nemeth_ids = nemeth_model.generate(
                **inputs, max_new_tokens=1280, num_beams=4, early_stopping=True
            )
            nemeth_output = nemeth_tokenizer.decode(
                nemeth_ids[0], skip_special_tokens=True
            )

            await websocket.send_json(
                {
                    "latex": latex,
                    "mathml": mathml,
                    "spoken_text": spoken_text,
                    "nemeth": nemeth_output,
                }
            )

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        await websocket.send_json({"error": str(e)})


# ▶️ Run server (inside script or externally)
if __name__ == "__main__":
    import sys

    if "idlelib" in sys.modules or "ipykernel" in sys.modules:
        nest_asyncio.apply()
        from fastapi.testclient import TestClient

        client = TestClient(app)
        print("Running inside interactive environment; not starting Uvicorn.")
    else:
        print("Starting server on http://0.0.0.0:8000")
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
# python -m uvicorn mains:app --host 0.0.0.0 --port 8000
