import React, { useState } from 'react';
import { QrReader } from 'react-qr-reader';
import axios from 'axios';

function QRScanner({ imageFile }) {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  // Handle image upload scan
  React.useEffect(() => {
    if (imageFile) {
      const formData = new FormData();
      formData.append('image', imageFile); // FIX: backend expects 'image'
      setLoading(true);
      axios.post('http://localhost:8000/scan_qr', formData)
        .then(res => {
          setResult(res.data);
        })
        .catch(err => {
          // FIX: handle backend error format
          if (err.response && err.response.data && err.response.data.message) {
            setResult({ error: err.response.data.message });
          } else {
            setResult({ error: 'Scan failed' });
          }
        })
        .finally(() => setLoading(false));
    }
  }, [imageFile]);

  // Handle webcam scan
  const handleScan = (data) => {
    if (data && !loading) {
      setLoading(true);
      axios.post('http://localhost:8000/scan_qr', { qr_data: data })
        .then(res => setResult(res.data))
        .catch(err => {
          if (err.response && err.response.data && err.response.data.message) {
            setResult({ error: err.response.data.message });
          } else {
            setResult({ error: 'Scan failed' });
          }
        })
        .finally(() => setLoading(false));
    }
  };

  return (
    <div className="scanner-area">
      {imageFile ? (
        loading ? <div>Scanning...</div> :
        result ? (
          <ResultDisplay result={result} />
        ) : null
      ) : (
        <>
          <QrReader
            constraints={{ facingMode: 'environment' }}
            onResult={(res, err) => {
              if (res?.text) handleScan(res.text);
            }}
            style={{ width: '100%' }}
          />
          {loading && <div>Scanning...</div>}
          {result && <ResultDisplay result={result} />}
        </>
      )}
    </div>
  );
}

function ResultDisplay({ result }) {
  if (result.error) return <div className="error">{result.error}</div>;
  return (
    <div className="result-card">
      <div><strong>QR Content:</strong> {result.qr_content}</div>
      <div><strong>Risk Level:</strong> {result.risk_level}</div>
      <div>
        <strong>Tips:</strong>
        <ul>
          {/* FIX: tips is an array */}
          {Array.isArray(result.tips)
            ? result.tips.map((tip, idx) => <li key={idx}>{tip}</li>)
            : <li>{result.tips}</li>
          }
        </ul>
      </div>
    </div>
  );
}

export default QRScanner;