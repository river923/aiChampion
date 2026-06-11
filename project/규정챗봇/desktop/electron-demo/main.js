import electron from "electron";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { spawn } from "node:child_process";
import fs from "node:fs";
import { ensurePackagedRuntimeData } from "./runtime-data.js";

const { app, BrowserWindow, ipcMain } = electron;
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
let backendBaseUrl = "http://127.0.0.1:8000"; // Default for dev
const allowedApiPaths = new Set([
  "/api/auth/csrf/",
  "/api/auth/login/",
  "/api/auth/status/",
  "/api/orgs/tree/",
  "/api/chat/ask/"
]);
const cookieJar = new Map();

function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 1280,
    height: 820,
    minWidth: 1024,
    minHeight: 680,
    title: "규정챗봇 데모",
    webPreferences: {
      preload: path.join(__dirname, "preload.cjs"),
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: true
    }
  });

  mainWindow.loadFile(path.join(__dirname, "renderer", "index.html"));
}

let backendProcess = null;

function startBackend(port) {
  const isDev = !app.isPackaged;
  if (isDev) {
    console.log(`Development mode: Assuming external dev server is running on port ${port}.`);
    return;
  }

  const userDataPath = app.getPath("userData");
  const resourcesPath = process.resourcesPath;
  const binaryName = process.platform === "win32" ? "backend.exe" : "backend";
  const binaryPath = path.join(resourcesPath, "bin", "backend", binaryName);
  const modelsDir = path.join(resourcesPath, "models");

  if (fs.existsSync(binaryPath)) {
    ensurePackagedRuntimeData(resourcesPath, userDataPath);
    console.log(`Starting bundled backend on port ${port}...`);
    // 전달할 인수: runserver 127.0.0.1:<port> --noreload
    backendProcess = spawn(binaryPath, ["runserver", `127.0.0.1:${port}`, "--noreload"], {
      env: {
        ...process.env,
        REGBOT_DATA_DIR: userDataPath,
        REGBOT_MODELS_DIR: modelsDir
      }
    });

    backendProcess.stdout.on("data", (data) => console.log(`Backend: ${data}`));
    backendProcess.stderr.on("data", (data) => console.error(`Backend Err: ${data}`));
    backendProcess.on("error", (error) => console.error("Backend spawn failed:", error));
  } else {
    console.log("Bundled backend not found at", binaryPath, "- assuming external dev server is running.");
  }
}

// 동적 포트 할당 함수
import net from "node:net";
function getAvailablePort() {
  return new Promise((resolve, reject) => {
    const server = net.createServer();
    server.unref();
    server.on("error", reject);
    server.listen(0, "127.0.0.1", () => {
      const port = server.address().port;
      server.close(() => {
        resolve(port);
      });
    });
  });
}

app.whenReady().then(async () => {
  ipcMain.handle("app:backendBaseUrl", () => backendBaseUrl);
  ipcMain.handle("app:apiRequest", (_event, request) => apiRequest(request));

  if (!app.isPackaged) {
    startBackend(8000); // Dev mode
  } else {
    try {
      const dynamicPort = await getAvailablePort();
      backendBaseUrl = `http://127.0.0.1:${dynamicPort}`;
      startBackend(dynamicPort);
      await waitForBackend();
    } catch (err) {
      console.error("Failed to get dynamic port:", err);
      startBackend(8000); // Fallback
      await waitForBackend();
    }
  }

  createWindow();
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});

app.on("quit", () => {
  if (backendProcess) {
    backendProcess.kill();
  }
});

app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

async function waitForBackend() {
  for (let attempt = 0; attempt < 40; attempt += 1) {
    try {
      const response = await fetch(`${backendBaseUrl}/api/auth/status/`);
      if (response.ok) {
        return;
      }
    } catch (_error) {
      await delay(500);
    }
  }
}

function delay(milliseconds) {
  return new Promise((resolve) => {
    setTimeout(resolve, milliseconds);
  });
}

async function apiRequest(request) {
  const parsed = parseApiRequest(request);
  const response = await fetch(`${backendBaseUrl}${parsed.path}`, {
    method: parsed.method,
    headers: buildHeaders(parsed),
    body: parsed.body
  });
  storeCookies(response.headers.get("set-cookie"));
  const text = await response.text();
  return {
    ok: response.ok,
    status: response.status,
    redirected: response.redirected,
    data: parseJson(text)
  };
}

function parseApiRequest(request) {
  if (!request || typeof request !== "object") {
    throw new Error("잘못된 API 요청입니다.");
  }
  const pathName = typeof request.path === "string" ? request.path : "";
  if (!allowedApiPaths.has(pathName)) {
    throw new Error("허용되지 않은 API 경로입니다.");
  }
  const method = typeof request.method === "string" ? request.method.toUpperCase() : "GET";
  if (!["GET", "POST"].includes(method)) {
    throw new Error("허용되지 않은 HTTP 메서드입니다.");
  }
  const body = request.body === undefined ? undefined : JSON.stringify(request.body);
  const csrfToken = typeof request.csrfToken === "string" ? request.csrfToken : "";
  return { path: pathName, method, body, csrfToken };
}

function buildHeaders(request) {
  const headers = {
    Accept: "application/json",
    Cookie: serializeCookies()
  };
  if (request.body !== undefined) {
    headers["Content-Type"] = "application/json";
  }
  if (request.csrfToken) {
    headers["X-CSRFToken"] = request.csrfToken;
  }
  return headers;
}

function storeCookies(setCookieHeader) {
  if (!setCookieHeader) {
    return;
  }
  const cookieParts = setCookieHeader.split(/,(?=\s*[^;,=\s]+=[^;,]+)/);
  for (const cookie of cookieParts) {
    const [pair] = cookie.split(";");
    const separatorIndex = pair.indexOf("=");
    if (separatorIndex <= 0) {
      continue;
    }
    cookieJar.set(pair.slice(0, separatorIndex).trim(), pair.slice(separatorIndex + 1).trim());
  }
}

function serializeCookies() {
  return [...cookieJar.entries()].map(([key, value]) => `${key}=${value}`).join("; ");
}

function parseJson(text) {
  if (!text) {
    return {};
  }
  try {
    return JSON.parse(text);
  } catch (_error) {
    return { error: "JSON 응답 형식이 올바르지 않습니다." };
  }
}
