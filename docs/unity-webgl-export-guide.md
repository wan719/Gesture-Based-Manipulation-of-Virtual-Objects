# Unity WebGL Export Guide

This guide explains how to export the Unity robot dog scene for the React dashboard.

## 1. Switch Build Platform

1. Open the Unity project.
2. Open `File -> Build Settings`.
3. Select `WebGL`.
4. Click `Switch Platform`.

## 2. Check Scene and RobotDog Object

1. Open the scene used for the robot dog demonstration.
2. Make sure the robot dog GameObject is named `RobotDog`.
3. Make sure `RobotDog` has `DogController` attached.
4. Make sure `DogController` contains:

```csharp
public void SetAction(string action)
{
    // idle / forward / backward / sit / wave
}
```

If the object name is not `RobotDog`, update `UNITY_TARGET_OBJECT` in:

```text
frontend/src/hooks/useUnityWebGL.js
```

If the exposed method is renamed, update `UNITY_TARGET_METHOD` in the same file.

## 3. Player Settings

In `Player Settings`, configure WebGL settings according to your local server:

- `Compression Format`: use `Disabled` for the easiest local test, or `Brotli/Gzip` if your server supports it.
- `Decompression Fallback`: enable it when using compressed builds and a simple local server.

## 4. Build Output

Click `Build` and export to:

```text
frontend/public/unity-build/
```

The exported folder should contain:

```text
frontend/public/unity-build/
├─ index.html
├─ Build/
└─ TemplateData/
```

The React dashboard currently tries to load:

```text
public/unity-build/Build/unity-build.loader.js
public/unity-build/Build/unity-build.data
public/unity-build/Build/unity-build.framework.js
public/unity-build/Build/unity-build.wasm
```

Current detected build files in this repository:

```text
frontend/public/unity-build/
├─ index.html
├─ Build/
│  ├─ unity-build.loader.js
│  ├─ unity-build.data
│  ├─ unity-build.framework.js
│  └─ unity-build.wasm
└─ TemplateData/
```

These files are not currently exported with `.br` or `.gz` suffixes, so the Vite dev server can serve them directly.

Unity may export different file names. If that happens, update `UNITY_BUILD_CONFIG` in:

```text
frontend/src/hooks/useUnityWebGL.js
```

If Unity exports `.br` or `.gz` files and the browser cannot load them from the Vite dev server, set:

```text
Player Settings -> Publishing Settings -> Compression Format = Disabled
```

Then export the WebGL build again. This is the easiest local-development option.

## 5. Runtime Link

React sends actions to Unity WebGL with:

```javascript
unityInstance.SendMessage("RobotDog", "SetAction", action);
```

Supported action strings:

```text
idle
forward
backward
sit
wave
```

The desktop Unity UDP path can stay in the project. WebGL does not use UDP sockets; it receives commands from React through `SendMessage`.
