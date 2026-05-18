import { useEffect, useRef, useState } from "react";

function CameraPanel({ currentState }) {
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const [isCameraOn, setIsCameraOn] = useState(false);
  const [cameraError, setCameraError] = useState("");

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setIsCameraOn(false);
  };

  const startCamera = async () => {
    setCameraError("");
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      setIsCameraOn(true);
    } catch {
      setCameraError("Camera permission denied or unavailable.");
      setIsCameraOn(false);
    }
  };

  useEffect(() => {
    return () => stopCamera();
  }, []);

  return (
    <section className="console-panel camera-panel panel-camera-accent">
      <div className="panel-heading">
        <div>
          <p className="panel-kicker">Gesture Camera Panel</p>
          <h2>Gesture Camera</h2>
        </div>
        <span className={`status-dot ${isCameraOn ? "online" : "standby"}`}>
          {isCameraOn ? "Camera On" : "Standby"}
        </span>
      </div>

      <div className="camera-frame">
        <div className="corner-mark top-left" />
        <div className="corner-mark top-right" />
        <div className="corner-mark bottom-left" />
        <div className="corner-mark bottom-right" />
        <video
          ref={videoRef}
          autoPlay
          muted
          playsInline
          className={isCameraOn ? "camera-video active" : "camera-video"}
        />
        {!isCameraOn && (
          <div className="camera-placeholder">
            <span className="scan-mark" />
            <strong>Camera Preview Offline</strong>
            <p>{cameraError || "Start Camera to show local browser preview."}</p>
          </div>
        )}
      </div>

      <div className="camera-actions">
        <button type="button" className="primary-button" onClick={startCamera}>
          Start Camera
        </button>
        <button type="button" className="secondary-button" onClick={stopCamera}>
          Stop Camera
        </button>
      </div>

      <div className="status-strip">
        <div>
          <span>Current Gesture</span>
          <strong>{currentState.gesture}</strong>
        </div>
        <div>
          <span>Stable Detection</span>
          <strong>Ready</strong>
        </div>
      </div>
    </section>
  );
}

export default CameraPanel;
