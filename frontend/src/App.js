import React, { useState } from 'react';
import QRScanner from './QRScanner';
import './App.css';

function App() {
  const [showScanner, setShowScanner] = useState(false);
  const [uploadedImage, setUploadedImage] = useState(null);

  const handleImageUpload = (e) => {
    if (e.target.files && e.target.files[0]) {
      setUploadedImage(e.target.files[0]);
      setShowScanner(false);
    }
  };

  return (
    <div className="app-bg">
      <header className="main-header">
        <span className="logo">ClickSafe Sri Lanka</span>
      </header>
      <div className="centered">
        <div className="header-card">
          <span>Phishing Detection</span>
          <button className="active-tab">QR Code Scanner</button>
        </div>
        <div className="card-row">
          <div className="card">
            <div className="card-title">Upload QR Code</div>
            <label className="upload-area">
              <input
                type="file"
                accept="image/png, image/jpeg, image/gif"
                style={{ display: 'none' }}
                onChange={handleImageUpload}
              />
              <div>
                <span className="upload-icon">&#8682;</span>
                <div>Click to upload QR code image</div>
                <div className="upload-hint">PNG, JPG, or GIF up to 10MB</div>
              </div>
            </label>
            {uploadedImage && (
              <QRScanner imageFile={uploadedImage} />
            )}
          </div>
          <div className="card">
            <div className="card-title">Camera Scanner</div>
            {!showScanner ? (
              <button className="camera-btn" onClick={() => setShowScanner(true)}>
                <span className="camera-icon">&#128247;</span> Start Camera
              </button>
            ) : (
              <QRScanner />
            )}
          </div>
        </div>
      </div>
      <footer className="watermark">
        &copy; {new Date().getFullYear()} ClickSafe Sri Lanka Team
      </footer>
    </div>
  );
}

export default App;