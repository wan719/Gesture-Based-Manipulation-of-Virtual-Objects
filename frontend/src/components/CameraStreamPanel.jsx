import { useEffect, useRef, useState } from "react";

const PYTHON_STREAM_URL = "http://127.0.0.1:8000/video_feed";

function CameraStreamPanel({ currentState, mode }) {
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const [streamAvailable, setStreamAvailable] = useState(mode === "live");
  const [localCameraOn, setLocalCameraOn] = useState(false);
  const [cameraError, setCameraError] = useState("");

  const stopLocalCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setLocalCameraOn(false);
  };

  const startLocalCamera = async () => {
    setCameraError("");
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      setLocalCameraOn(true);
    } catch {
      setCameraError("Camera permission denied or unavailable.");
    }
  };

  useEffect(() => {
    return () => stopLocalCamera();
  }, []);

  useEffect(() => {
    if (mode === "live") {
      setStreamAvailable(true);
    }
  }, [mode]);

  const stableCount = currentState.stableCount ?? 0;
  const requiredStableFrames = currentState.requiredStableFrames ?? 4;

  return (
    <section className="console-panel camera-panel panel-camera-accent">
      <div className="panel-heading">
        <div>
          <p className="panel-kicker">Python Stream Panel</p>
          <h2>Python Gesture Recognition Stream</h2>
        </div>
        <span className={`status-dot ${streamAvailable || localCameraOn ? "online" : "standby"}`}>
          {streamAvailable ? "MJPEG" : localCameraOn ? "Local Camera" : "Waiting"}
        </span>
      </div>

      <div className="camera-frame">
        <div className="corner-mark top-left" />
        <div className="corner-mark top-right" />
        <div className="corner-mark bottom-left" />
        <div className="corner-mark bottom-right" />

        {mode === "live" && streamAvailable && (
          <img
            className="python-stream"
            src={`${PYTHON_STREAM_URL}?t=${Date.now()}`}
            alt="Python MediaPipe gesture recognition stream"
            onError={() => setStreamAvailable(false)}
          />
        )}

        {(!streamAvailable || mode === "demo") && localCameraOn && (
          <video ref={videoRef} autoPlay muted playsInline className="camera-video active" />
        )}

        {(!streamAvailable || mode === "demo") && !localCameraOn && (
          <div className="camera-placeholder">
            <span className="scan-mark" />
            <strong>Waiting for Python camera stream...</strong>
            <p>{cameraError || "Use local camera fallback when the Python stream is unavailable."}</p>
          </div>
        )}
      </div>

      <div className="camera-actions">
        <button type="button" className="primary-button" onClick={startLocalCamera}>
          Start Local Camera
        </button>
        <button type="button" className="secondary-button" onClick={stopLocalCamera}>
          Stop Local Camera
        </button>
      </div>

      <div className="status-strip">
        <div>
          <span>Current Gesture</span>
          <strong>{currentState.gesture}</strong>
        </div>
        <div>
          <span>Stable Count</span>
          <strong>{stableCount} / {requiredStableFrames}</strong>
        </div>
      </div>
    </section>
  );
}

export default CameraStreamPanel;
