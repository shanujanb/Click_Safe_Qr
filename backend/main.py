# This is the API backend used by the frontend. Ensure this is the backend you run for the app.

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json
from qr_module import scan_qr_pyzbar, preprocess_and_decode_opencv, check_url_safety

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only. Restrict in production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/scan_qr/")
async def scan_qr(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        qr_data = scan_qr_pyzbar(image_bytes)
        decoded_data = preprocess_and_decode_opencv(image_bytes)
        url = decoded_data or (qr_data[0] if qr_data else "")
        risk = check_url_safety(url) if url else "low"
        try:
            with open("backend/qr_tips.json", encoding="utf-8") as f:
                tips = json.load(f)
        except Exception:
            tips = {
                "high": {"en": "", "si": "", "ta": ""},
                "medium": {"en": "", "si": "", "ta": ""},
                "low": {"en": "", "si": "", "ta": ""}
            }
        return {
            "qr_data": qr_data,
            "decoded_data": decoded_data,
            "risk": risk,
            "tips": tips.get(risk, {"en": "", "si": "", "ta": ""})
        }
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})