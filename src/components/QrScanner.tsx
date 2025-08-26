import React, { useEffect, useRef, useState } from "react";
import { Html5Qrcode } from "html5-qrcode";

const QrScanner: React.FC<{ onScan: (data: string) => void }> = ({ onScan }) => {
  const [error, setError] = useState<string | null>(null);
  const [scanning, setScanning] = useState(true);
  const qrReaderId = "qr-reader-html5";
  const html5QrCodeRef = useRef<Html5Qrcode | null>(null);

  useEffect(() => {
    let isMounted = true;
    if (scanning) {
      // Ensure the div exists before starting
      const qrDiv = document.getElementById(qrReaderId);
      if (!qrDiv) {
        setError("QR scanner element not found.");
        return;
      }
      const html5QrCode = new Html5Qrcode(qrReaderId);
      html5QrCodeRef.current = html5QrCode;
      html5QrCode
        .start(
          { facingMode: "environment" },
          {
            fps: 10,
            qrbox: { width: 250, height: 250 },
          },
          (decodedText) => {
            if (isMounted) {
              setScanning(false);
              html5QrCode.stop().catch(() => {});
              onScan(decodedText);
            }
          },
          (scanError) => {
            // Optionally log scan errors for debugging
            // setError("Scan error: " + scanError); // Uncomment for verbose errors
          }
        )
        .catch((err) => {
          setError("Camera error: " + err);
        });
    }
    return () => {
      isMounted = false;
      html5QrCodeRef.current?.stop().catch(() => {});
      html5QrCodeRef.current?.clear().catch(() => {});
    };
  }, [scanning, onScan]);

  return (
    <div>
      <div id={qrReaderId} style={{ width: 300, height: 300 }} />
      {error && <div style={{ color: "red" }}>{error}</div>}
      {!scanning && (
        <button
          onClick={() => {
            setError(null);
            setScanning(true);
          }}
        >
          Scan Again
        </button>
      )}
    </div>
  );
};

export default QrScanner;