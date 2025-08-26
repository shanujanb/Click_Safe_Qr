# --- FastAPI is used for building the backend API ---
import os
import shutil
import tempfile
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Body

# --- Pillow (PIL) and OpenCV are used for image processing ---
from PIL import Image
import cv2
import numpy as np

# --- pyzbar is used for decoding QR codes from images ---
# (Alternative: 'qrcode' library can also be used for QR decoding)
from pyzbar.pyzbar import decode

# --- requests is used for making HTTP requests (e.g., to VirusTotal API) ---
import requests
import json

# --- Initialize FastAPI app ---
app = FastAPI()

# --- Enable CORS so frontend (React.js) can talk to backend ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development; restrict in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Load QR safety tips from a JSON file (supports Sinhala, Tamil, English) ---
with open("qr_tips.json", "r", encoding="utf-8") as f:
    tips_data = json.load(f)

# --- VirusTotal API key (used for URL safety checks) ---
VIRUSTOTAL_API_KEY = "9d25e0ab0b8a3f4c9f2d1631f9f8ddf0004652fc45b04886ce3ab6a25cbb71d2"

def check_url_virustotal(url):
    """
    Checks the safety of a URL using the VirusTotal API.
    Returns a risk level: 'high', 'medium', or 'low'.
    """
    vt_url = "https://www.virustotal.com/api/v3/urls"
    try:
        # VirusTotal expects the URL in a specific format
        resp = requests.post(
            vt_url,
            headers={"x-apikey": VIRUSTOTAL_API_KEY},
            data={"url": url},
            timeout=2
        )
        if resp.status_code == 200:
            vt_id = resp.json()["data"]["id"]
            # Get analysis results for the submitted URL
            analysis = requests.get(
                f"https://www.virustotal.com/api/v3/analyses/{vt_id}",
                headers={"x-apikey": VIRUSTOTAL_API_KEY},
                timeout=2
            )
            if analysis.status_code == 200:
                stats = analysis.json()["data"]["attributes"]["stats"]
                malicious = stats.get("malicious", 0)
                suspicious = stats.get("suspicious", 0)
                harmless = stats.get("harmless", 0)
                # If any malicious or suspicious reports, mark as high risk
                if malicious > 0 or suspicious > 0:
                    return "high"
                # If marked harmless, mark as low risk
                elif harmless > 0:
                    return "low"
                # Otherwise, medium risk
                else:
                    return "medium"
        # If anything fails, default to medium risk
        return "medium"
    except Exception:
        # If an error occurs (e.g., network issue), default to medium risk
        return "medium"

def get_tips(risk_level, lang="en"):
    """
    Returns a list of safety tips based on risk level and language.
    """
    return tips_data.get(lang, {}).get(risk_level, [])

@app.post("/scan_qr")
async def scan_qr(
    image: UploadFile = File(None),
    request: Request = None,
    lang: str = "en"
):
    """
    API endpoint to scan a QR code.
    Accepts either an uploaded image file or QR data from webcam (JSON).
    Returns the decoded QR content, risk level, and safety tips.
    """
    # --- Create a temporary directory for processing images ---
    sandbox_dir = os.path.join(os.getcwd(), "sandbox")
    os.makedirs(sandbox_dir, exist_ok=True)
    temp_file = None
    try:
        qr_content = None
        # --- If an image file is uploaded (from frontend) ---
        if image is not None:
            # Save the uploaded image to a temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, dir=sandbox_dir, suffix=".png")
            contents = await image.read()
            temp_file.write(contents)
            temp_file.close()
            # Read image using OpenCV
            img = cv2.imread(temp_file.name)
            # Try to decode QR code using pyzbar
            qr_codes = decode(img)
            if not qr_codes:
                # If pyzbar fails, try using Pillow (sometimes works better)
                pil_img = Image.open(temp_file.name)
                qr_codes = decode(np.array(pil_img))
            if not qr_codes:
                # If no QR code found, return error
                os.remove(temp_file.name)
                return JSONResponse({"error": "No QR code detected"}, status_code=400)
            # Get the decoded QR content (as text)
            qr_content = qr_codes[0].data.decode("utf-8")
            os.remove(temp_file.name)
        else:
            # --- If QR data is sent directly (e.g., from webcam scan) ---
            data = await request.json()
            qr_data = data.get("qr_data")
            if not qr_data:
                return JSONResponse({"error": "No QR data provided"}, status_code=400)
            qr_content = qr_data

        # --- Check if the QR content is a URL and assess its risk ---
        if qr_content and qr_content.startswith("http"):
            risk_level = check_url_virustotal(qr_content)
        else:
            # If not a URL, assume low risk
            risk_level = "low"

        # --- Get safety tips based on risk level and language ---
        tips = get_tips(risk_level, lang)
        return {
            "qr_content": qr_content,
            "risk_level": risk_level,
            "tips": tips
        }
    except Exception as e:
        # --- Clean up temporary file if an error occurs ---
        if temp_file and os.path.exists(temp_file.name):
            os.remove(temp_file.name)
        # Return error message
        return JSONResponse({"error": str(e)}, status_code=500)

# --- Note: For database storage, you would use PostgreSQL (production) or SQLite (development).
# --- For scam message classification, you would use scikit-learn or XLM-RoBERTa (not shown here).
# --- For QR scanning from camera, use 'react-qr-reader' in the frontend.
# --- For multilingual support, use 'i18next' in the frontend.
# --- For deployment, use Docker, Railway.app, Render.com, etc.

# Standalone FastAPI backend. Not used by the frontend. You may remove this file if not needed.