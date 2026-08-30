'use strict';
const { contextBridge, ipcRenderer } = require('electron');

// The renderer gets a named surface, never Node itself.
contextBridge.exposeInMainWorld('studio', {
  getConfig: () => ipcRenderer.invoke('config:get'),
  pickSuite: () => ipcRenderer.invoke('suite:pick'),
  readSuite: (suitePath) => ipcRenderer.invoke('suite:read', suitePath),
  pickFolder: () => ipcRenderer.invoke('folder:pick'),
  launch: (payload) => ipcRenderer.invoke('session:launch', payload),
  openPath: (target) => ipcRenderer.invoke('shell:openPath', target),
  openWorkflow: (suitePath) => ipcRenderer.invoke('workflow:open', suitePath),
  newWorkflow: (suitePath) => ipcRenderer.invoke('workflow:new', suitePath),
  saveWorkflow: (payload) => ipcRenderer.invoke('workflow:save', payload),
  validateWorkflow: (payload) => ipcRenderer.invoke('workflow:validate', payload),
});
