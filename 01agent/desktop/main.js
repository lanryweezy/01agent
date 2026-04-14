import { app, Menu, Tray, ipcMain, globalShortcut, nativeImage } from 'electron';
import path from 'path';
import { fileURLToPath } from 'url';
import isDev from 'electron-is-dev';
import Store from 'electron-store';
import constants from './electron/utils/constants.js';
import http from 'http';
import { v4 as uuidv4 } from 'uuid';
import {
  createWindow,
  createOverlayWindow,
  expandMinimizeOverlay,
  launchBackgroundAuthWindow,
  launchBackgroundAgentWindow,
  bgAgentWindow,
} from './electron/main-process/windowManager.js';
import {
  startAiAgent,
  stopAiAgent,
  aiagentProcess,
} from './electron/main-process/processManager.js';
import { registerIpcHandlers } from './electron/main-process/ipcHandlers.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const store = new Store();

let mainWindow;
let overlayWindow;
let tray;
let bgSetupWindow;
let readyToClose = false;

function ensureDeviceId() {
  let deviceId = store.get(constants.DEVICE_ID_STORE_KEY);
  if (!deviceId) {
    deviceId = uuidv4();
    store.set(constants.DEVICE_ID_STORE_KEY, deviceId);
    console.log(`[Device ID created]: ${deviceId}`);
  } else {
    console.log(`[Device ID exists]: ${deviceId}`);
  }
}

function waitForNoVNCPortReady(port, timeout = 10000, interval = 300) {
  const deadline = Date.now() + timeout;

  return new Promise((resolve, reject) => {
    const check = () => {
      const req = http.get({ hostname: '127.0.0.1', port, path: '/', timeout: 1000 }, (res) => {
        res.destroy();
        resolve(true); // Port is ready
      });

      req.on('error', (err) => {
        if (Date.now() > deadline) return reject(new Error('Timed out waiting for noVNC'));
        setTimeout(check, interval);
      });

      req.end();
    };

    check();
  });
}

const createAppMenu = () => {
  const template = [
    {
      label: 'App',
      submenu: [
        {
          label: 'Logout',
          click: () => {
            if (overlayWindow) {
              overlayWindow.close();
            }
            mainWindow?.webContents.send('trigger-logout');
          },
        },
        { role: 'quit' },
      ],
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload' },
        { role: 'togglefullscreen' },
        // { role: 'toggledevtools' },
      ],
    },
  ];
  Menu.setApplicationMenu(Menu.buildFromTemplate(template));
};

const gotLock = app.requestSingleInstanceLock();
if (!gotLock) {
  app.quit();
} else {
  app.on('second-instance', () => {
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.focus();
    }
  });
}

app.whenReady().then(() => {
  ensureDeviceId();
  mainWindow = createWindow(readyToClose, ipcMain);

  // Create System Tray
  const iconPath = path.join(__dirname, '01agent-app', 'public', 'favicon.ico');
  const trayIcon = nativeImage.createFromPath(iconPath);
  tray = new Tray(trayIcon);

  const trayMenu = Menu.buildFromTemplate([
    { label: 'Show App', click: () => mainWindow.show() },
    { label: 'Quit', click: () => {
        readyToClose = true;
        app.quit();
    }}
  ]);

  tray.setToolTip('01Agent AI Assistant');
  tray.setContextMenu(trayMenu);
  tray.on('click', () => mainWindow.show());

  // Register Global Hotkey: Alt+Space (or Command+Space on Mac) to focus/unfocus
  const shortcut = process.platform === 'darwin' ? 'Command+Space' : 'Alt+Space';
  globalShortcut.register(shortcut, () => {
    if (mainWindow) {
      if (mainWindow.isVisible() && mainWindow.isFocused()) {
        mainWindow.hide();
      } else {
        mainWindow.show();
        mainWindow.focus();
      }
    }
  });

  if (store.get(constants.ACCESS_TOKEN_STORE_KEY)) {
    overlayWindow = createOverlayWindow();
  }
  createAppMenu();
  registerIpcHandlers(store, mainWindow, overlayWindow, bgSetupWindow, bgAgentWindow, expandMinimizeOverlay);

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      mainWindow = createWindow(readyToClose, ipcMain);
      overlayWindow = createOverlayWindow();
    }
  });
});

app.on('window-all-closed', () => {
    stopAiAgent();
    globalShortcut.unregisterAll();
    if (process.platform !== 'darwin') app.quit();
});

mainWindow.on('closed', () => {
    mainWindow = null;

    if (overlayWindow && !overlayWindow.isDestroyed()) {
        overlayWindow.close();
    }
    if (bgAgentWindow && !bgAgentWindow.isDestroyed()) {
        bgAgentWindow.close();
    }
    if (bgSetupWindow && !bgSetupWindow.isDestroyed()) {
        bgSetupWindow.close();
    }
    if (backgroundAuthWindow && !backgroundAuthWindow.isDestroyed()) {
        backgroundAuthWindow.close();
    }
});
