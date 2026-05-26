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
      setCameraError("摄像头权限被拒绝或设备不可用。");
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
          <p className="panel-kicker">手势摄像头面板</p>
          <h2>手势摄像头</h2>
        </div>
        <span className={`status-dot ${isCameraOn ? "online" : "standby"}`}>
          {isCameraOn ? "摄像头已开启" : "待机"}
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
            <strong>摄像头预览未开启</strong>
            <p>{cameraError || "点击启动摄像头，显示浏览器本地预览。"}</p>
          </div>
        )}
      </div>

      <div className="camera-actions">
        <button type="button" className="primary-button" onClick={startCamera}>
          启动摄像头
        </button>
        <button type="button" className="secondary-button" onClick={stopCamera}>
          关闭摄像头
        </button>
      </div>

      <div className="status-strip">
        <div>
          <span>当前手势</span>
          <strong>{currentState.gesture}</strong>
        </div>
        <div>
          <span>稳定识别</span>
          <strong>就绪</strong>
        </div>
      </div>
    </section>
  );
}

export default CameraPanel;
