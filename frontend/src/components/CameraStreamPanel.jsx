import { useEffect, useRef, useState } from "react";

const PYTHON_STREAM_URL = "http://127.0.0.1:8000/video_feed";

function CameraStreamPanel({ currentState }) {
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const [streamAvailable, setStreamAvailable] = useState(true);
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
      setCameraError("摄像头权限被拒绝或设备不可用。");
    }
  };

  useEffect(() => {
    return () => stopLocalCamera();
  }, []);

  const stableCount = currentState.stableCount ?? 0;
  const requiredStableFrames = currentState.requiredStableFrames ?? 4;

  return (
    <section className="console-panel camera-panel panel-camera-accent">
      <div className="panel-heading">
        <div>
          <p className="panel-kicker">Python 识别画面</p>
          <h2>Python 手势识别视频流</h2>
        </div>
        <span className={`status-dot ${streamAvailable || localCameraOn ? "online" : "standby"}`}>
          {streamAvailable ? "MJPEG" : localCameraOn ? "本地摄像头" : "等待中"}
        </span>
      </div>

      <div className="camera-frame">
        <div className="corner-mark top-left" />
        <div className="corner-mark top-right" />
        <div className="corner-mark bottom-left" />
        <div className="corner-mark bottom-right" />

        {streamAvailable && (
          <img
            className="python-stream"
            src={`${PYTHON_STREAM_URL}?t=${Date.now()}`}
            alt="Python MediaPipe 手势识别画面"
            onError={() => setStreamAvailable(false)}
          />
        )}

        {!streamAvailable && localCameraOn && (
          <video ref={videoRef} autoPlay muted playsInline className="camera-video active" />
        )}

        {!streamAvailable && !localCameraOn && (
          <div className="camera-placeholder">
            <span className="scan-mark" />
            <strong>等待 Python 摄像头视频流...</strong>
            <p>{cameraError || "Python 视频流不可用时，可使用本地摄像头预览。"}</p>
          </div>
        )}
      </div>

      <div className="camera-actions">
        <button type="button" className="primary-button" onClick={startLocalCamera}>
          启动本地摄像头
        </button>
        <button type="button" className="secondary-button" onClick={stopLocalCamera}>
          关闭本地摄像头
        </button>
      </div>

      <div className="status-strip">
        <div>
          <span>当前手势</span>
          <strong>{currentState.gesture}</strong>
        </div>
        <div>
          <span>稳定帧数</span>
          <strong>{stableCount} / {requiredStableFrames}</strong>
        </div>
      </div>
    </section>
  );
}

export default CameraStreamPanel;
