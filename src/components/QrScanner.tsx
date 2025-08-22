import React, { useState } from "react";
// If you haven't installed, run: npm install @blackbox-vision/react-qr-reader
import { QrReader } from "@blackbox-vision/react-qr-reader";
import axios from "axios";

const QrScanner = () => {
  const [result, setResult] = useState("");
  const [risk, setRisk] = useState("");
  const [tips, setTips] = useState({ en: "", si: "", ta: "" });
  const [error, setError] = useState("");
  const [scanAttempted, setScanAttempted] = useState(false);

  const handleResult = async (scanResult: any, error: any) => {
    setScanAttempted(true);
    console.log("handleResult called with:", scanResult, error); // Debug log
    if (error) {
      setError("Camera error or not available.");
      return;
    }
    if (!scanResult?.text || scanResult.text === result) return;
    setResult(scanResult.text);
    setError("");
    try {
      const response = await axios.post(
        "/api/scan_qr/",
        { qr_string: scanResult.text },
        { headers: { "Content-Type": "application/json" } }
      );
      setRisk(response.data?.risk ?? "");
      setTips(response.data?.tips ?? { en: "", si: "", ta: "" });
    } catch (err: any) {
      setError("Scan failed or server error.");
      setRisk("");
      setTips({ en: "", si: "", ta: "" });
    }
  };

  return (
    <div>
      <div style={{ width: "100%" }}>
        <QrReader
          constraints={{ facingMode: "environment" }}
          onResult={handleResult}
        />
      </div>
      {error && <p style={{ color: "red" }}>{error}</p>}
      {/* Show a message if scan attempted but no QR detected */}
      {scanAttempted && !result && (
        <p style={{ color: "orange" }}>
          No QR code detected. Please ensure the QR code is visible and try again.
        </p>
      )}
      <div>
        <p>Result: {result}</p>
        <p>Risk: {risk}</p>
        <p>Tips (EN): {tips.en}</p>
        <p>Tips (SI): {tips.si}</p>
        <p>Tips (TA): {tips.ta}</p>
      </div>
    </div>
  );
};

export default QrScanner;