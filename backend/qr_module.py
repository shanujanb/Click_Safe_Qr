import cv2
import numpy as np
from pyzbar.pyzbar import decode
from PIL import Image, UnidentifiedImageError
import requests
import cProfile
import io

VIRUSTOTAL_API_KEY = "YOUR_API_KEY"
VIRUSTOTAL_URL = "https://www.virustotal.com/api/v3/urls"

def scan_qr_pyzbar(image_bytes):
    try:
        image = Image.open(io.BytesIO(image_bytes))
        qr_codes = decode(image)
        return [qr.data.decode('utf-8') for qr in qr_codes]
    except UnidentifiedImageError:
        return []
    except Exception:
        return []

def preprocess_and_decode_opencv(image_bytes):
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return ""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5,5), 0)
        detector = cv2.QRCodeDetector()
        data, _, _ = detector.detectAndDecode(blur)
        return data
    except Exception:
        return ""

def check_url_safety(url):
    if not url:
        return "low"
    try:
        resp = requests.post(
            VIRUSTOTAL_URL,
            headers={"x-apikey": VIRUSTOTAL_API_KEY},
            data={"url": url},
            timeout=10
        )
        result = resp.json()
        stats = result.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
        malicious = stats.get("malicious", 0)
        suspicious = stats.get("suspicious", 0)
        if malicious > 0:
            return "high"
        elif suspicious > 0:
            return "medium"
        else:
            return "low"
    except Exception:
        return "low"

def sandbox_test(image_bytes):
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img = img.convert("L").resize((300, 300))
        arr = np.array(img)
        detector = cv2.QRCodeDetector()
        data, _, _ = detector.detectAndDecode(arr)
        return data
    except Exception:
        return ""

def profile_qr_module(image_bytes):
    profiler = cProfile.Profile()
    profiler.enable()
    result = scan_qr_pyzbar(image_bytes)
    profiler.disable()
    return result