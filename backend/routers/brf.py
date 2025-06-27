from fastapi import APIRouter, WebSocket
import uuid, os, base64
from utils.braille import convert_unicode_to_ascii_braille

router = APIRouter()

BRF_STORAGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../brf_files")
os.makedirs(BRF_STORAGE_DIR, exist_ok=True)

@router.websocket("/ws/brf")
async def websocket_generate_brf(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        unicode_braille = data.get("nemeth")

        if not unicode_braille:
            await websocket.send_json({"error": "Nemeth Braille string is required"})
            return

        ascii_braille = convert_unicode_to_ascii_braille(unicode_braille)
        file_id = str(uuid.uuid4())
        filename = f"{file_id}.brf"
        filepath = os.path.join(BRF_STORAGE_DIR, filename)

        # Save .brf file (max 80 chars per line)
        with open(filepath, "w", encoding="ascii") as f:
            for i in range(0, len(ascii_braille), 80):
                f.write(ascii_braille[i:i + 80] + "\n")

        # Encode file content to base64
        with open(filepath, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")

        await websocket.send_json({
            "message": "BRF generated successfully",
            "filename": filename,
            "base64": encoded,
        })

    except Exception as e:
        await websocket.send_json({"error": str(e)})
    finally:
        await websocket.close()
