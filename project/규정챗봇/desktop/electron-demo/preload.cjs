const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("regbot", {
  backendBaseUrl: () => ipcRenderer.invoke("app:backendBaseUrl"),
  apiRequest: (request) => ipcRenderer.invoke("app:apiRequest", request)
});
