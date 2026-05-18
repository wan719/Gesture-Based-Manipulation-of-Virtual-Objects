import { useCallback, useEffect, useRef, useState } from "react";

export const UNITY_TARGET_OBJECT = "RobotDog";
export const UNITY_TARGET_METHOD = "SetAction";
export const UNITY_CANVAS_ID = "unity-canvas";

const UNITY_BUILD_VERSION = "20260518-170326";

function withBuildVersion(path) {
  return `${path}?v=${UNITY_BUILD_VERSION}`;
}

export const UNITY_BUILD_CONFIG = {
  loaderUrl: withBuildVersion("/unity-build/Build/unity-build.loader.js"),
  dataUrl: withBuildVersion("/unity-build/Build/unity-build.data"),
  frameworkUrl: withBuildVersion("/unity-build/Build/unity-build.framework.js"),
  codeUrl: withBuildVersion("/unity-build/Build/unity-build.wasm"),
  streamingAssetsUrl: "/unity-build/StreamingAssets",
  companyName: "GestureDashboard",
  productName: "VirtualRobotDog",
  productVersion: "1.0",
  cacheControl: () => "no-store",
};

const UNITY_LOADER_PROMISE_KEY = "__gestureDashboardUnityLoaderPromise";

function getCreateUnityInstance() {
  return window.createUnityInstance || globalThis.createUnityInstance;
}

function loadUnityLoader(loaderUrl) {
  if (getCreateUnityInstance()) {
    console.info("[UnityWebGL] loader already available");
    return Promise.resolve();
  }

  if (window[UNITY_LOADER_PROMISE_KEY]) {
    console.info("[UnityWebGL] reusing Unity loader promise");
    return window[UNITY_LOADER_PROMISE_KEY];
  }

  console.info("[UnityWebGL] start loading Unity loader:", loaderUrl);

  window[UNITY_LOADER_PROMISE_KEY] = new Promise((resolve, reject) => {
    const existingScript = document.querySelector(`script[data-unity-loader="${loaderUrl}"]`);

    if (existingScript?.dataset.loaded === "true") {
      if (getCreateUnityInstance()) {
        console.info("[UnityWebGL] existing Unity loader is loaded");
        resolve();
      } else {
        reject(new Error("Unity loader script loaded, but createUnityInstance is undefined."));
      }
      return;
    }

    const script = existingScript || document.createElement("script");
    script.src = loaderUrl;
    script.async = true;
    script.dataset.unityLoader = loaderUrl;

    script.onload = () => {
      script.dataset.loaded = "true";
      console.info("[UnityWebGL] Unity loader loaded successfully:", loaderUrl);
      if (getCreateUnityInstance()) {
        resolve();
      } else {
        reject(new Error("loader.js loaded, but createUnityInstance is undefined."));
      }
    };

    script.onerror = () => {
      const message = `Unity loader failed to load: ${loaderUrl}`;
      console.error("[UnityWebGL] Unity load error:", message);
      reject(new Error(message));
    };

    if (!existingScript) {
      document.body.appendChild(script);
    }
  });

  window[UNITY_LOADER_PROMISE_KEY] = window[UNITY_LOADER_PROMISE_KEY].catch((err) => {
    delete window[UNITY_LOADER_PROMISE_KEY];
    throw err;
  });

  return window[UNITY_LOADER_PROMISE_KEY];
}

export default function useUnityWebGL(canvasRef) {
  const unityInstanceRef = useRef(null);
  const bootIdRef = useRef(0);
  const [status, setStatus] = useState("idle");
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState("");
  const [bannerMessage, setBannerMessage] = useState("");

  useEffect(() => {
    const bootId = bootIdRef.current + 1;
    bootIdRef.current = bootId;
    let disposed = false;

    async function bootUnity() {
      const canvas = canvasRef.current;
      if (!canvas) return;

      setStatus("loading");
      setProgress(0);
      setError("");
      setBannerMessage("");

      try {
        if (!canvas.id) {
          canvas.id = UNITY_CANVAS_ID;
        }
        canvas.tabIndex = canvas.tabIndex || 0;

        await loadUnityLoader(UNITY_BUILD_CONFIG.loaderUrl);
        if (disposed || bootIdRef.current !== bootId) return;

        const createUnityInstance = getCreateUnityInstance();
        if (!createUnityInstance) {
          throw new Error("createUnityInstance is undefined after loader.js onload.");
        }

        const unityConfig = {
          ...UNITY_BUILD_CONFIG,
          showBanner: (message, type) => {
            const text = `[${type || "info"}] ${message}`;
            console[type === "error" ? "error" : "warn"]("[UnityWebGL] Unity banner:", text);
            setBannerMessage(text);
            if (type === "error") {
              setError(text);
            }
          },
        };

        console.info("[UnityWebGL] createUnityInstance start", unityConfig);
        const instance = await createUnityInstance(
          canvas,
          unityConfig,
          (value) => {
            if (!disposed && bootIdRef.current === bootId) {
              setProgress(Math.round(value * 100));
            }
          }
        );

        if (disposed || bootIdRef.current !== bootId) {
          if (instance?.Quit) instance.Quit();
          return;
        }

        unityInstanceRef.current = instance;
        setProgress(100);
        setStatus("ready");
        console.info("[UnityWebGL] Unity Ready");
      } catch (err) {
        if (!disposed && bootIdRef.current === bootId) {
          const message = err?.message || String(err) || "Unknown Unity load error";
          console.error("[UnityWebGL] Unity load error:", err);
          setStatus("error");
          setError(`${message}\n\nIf this persists, press Ctrl+F5. The Unity canvas must keep id="${UNITY_CANVAS_ID}" so Unity can register input events.`);
        }
      }
    }

    bootUnity();

    return () => {
      disposed = true;
      if (unityInstanceRef.current?.Quit) {
        unityInstanceRef.current.Quit();
      }
      unityInstanceRef.current = null;
    };
  }, [canvasRef]);

  const sendAction = useCallback((action) => {
    if (!action || !unityInstanceRef.current?.SendMessage) {
      return false;
    }

    try {
      console.info(
        `[UnityWebGL] SendMessage action: ${UNITY_TARGET_OBJECT}.${UNITY_TARGET_METHOD}(${action})`
      );
      unityInstanceRef.current.SendMessage(UNITY_TARGET_OBJECT, UNITY_TARGET_METHOD, action);
      return true;
    } catch (err) {
      console.error(
        `[UnityWebGL] Unity SendMessage failed: ${UNITY_TARGET_OBJECT}.${UNITY_TARGET_METHOD}(${action})`,
        err
      );
      return false;
    }
  }, []);

  return {
    status,
    progress,
    error,
    bannerMessage,
    sendAction,
    unityInstance: unityInstanceRef.current,
  };
}
